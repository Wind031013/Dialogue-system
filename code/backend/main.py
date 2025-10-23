from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import os

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

from datetime import datetime
import logging
import json

fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "password": "123",
        "avatar": None
    }
}

# 配置参数
class Config:
    MODEL_NAME = os.getenv("MODEL_PATH", r"C:\Users\wind\.cache\modelscope\hub\models\Qwen\Qwen3-0___6B")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 2048))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", 6))
    
    SYSTEM_PROMPT = """
你是小说《斗破苍穹》中的角色药老，是主角萧炎的老师。

说话风格：
    自称： 永远自称老夫。
    称呼萧炎：小家伙，小炎子，傻小子。
    语气词：频繁使用"嘿嘿"，"呵呵"，"啧啧"
时刻记住自己是药老，使用上述的说话风格。

性格：喜欢调侃打趣萧炎。
对话节奏：回答要切中要害，但不必过分追求简短而失去角色魅力。

在进行提问时为为你提供可能相关的背景信息，请自行判断是否需要使用这些信息。

背景信息相关注意事项：
    人格化表达：绝对禁止机械复述任何背景信息，你必须将所有知识用药老的风格人格化表达出来。
    知识边界：你只能回答你背景信息中涉及的问题，对于超出你已知范围的内容，你必须以药老的方式拒绝回答。如：
        user："帮我写一份Python代码实现快速排序。" assistant："哼，净说些为师听不懂的怪话。什么'派森'、'快排'，现在你的脑子里只应该有练气和炼药！莫要分心！"

在回答问题时时刻记住你是药老，使用上述的行为模式跟我对话。

现在，我是萧炎，请开始我们的对话。
"""

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    user: Optional[User] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None

class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色: user, assistant")
    content: str = Field(..., description="消息内容")
    time: Optional[str] = Field(None, description="消息时间")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="对话历史")
    max_tokens: Optional[int] = Field(512, ge=1, le=2048, description="最大生成长度")
    temperature: Optional[float] = Field(0.7, ge=0.1, le=2.0, description="温度参数")
    top_p: Optional[float] = Field(0.9, ge=0.1, le=1.0, description="Top-p采样参数")
    repetition_penalty: Optional[float] = Field(1.1, ge=1.0, le=2.0, description="重复惩罚")

class ChatResponse(BaseModel):
    role: str = Field(..., description="回复角色")
    content: str = Field(..., description="回复内容")
    time: str = Field(..., description="回复时间")
    status: str = Field("success", description="响应状态")
    tokens_used: Optional[int] = Field(None, description="使用的token数量")

class SimpleChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    max_tokens: Optional[int] = Field(512, ge=1, le=2048, description="最大生成长度")

class HealthResponse(BaseModel):
    status: str = Field(..., description="服务状态")
    model_loaded: bool = Field(..., description="模型是否加载")
    timestamp: str = Field(..., description="检查时间")
    device: Optional[str] = Field(None, description="模型运行设备")

# 全局模型变量
class ModelManager:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = None
        self.is_loaded = False
    
    def load_model(self):
        """加载模型和分词器"""
        try:
            logger.info("正在加载分词器...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                Config.MODEL_NAME,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("正在加载基础模型...")
            self.model = AutoModelForCausalLM.from_pretrained(
                Config.MODEL_NAME,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            # 检查是否有可用的LoRA权重
            # lora_path = "lora_Qwen3-8B_yaolao"
            # if os.path.exists(lora_path):
            #     logger.info("正在加载LoRA权重...")
            #     self.model = PeftModel.from_pretrained(
            #         self.model,
            #         lora_path,
            #         torch_dtype=torch.float16
            #     )
            
            self.model.eval()
            self.device = self.model.device
            self.is_loaded = True
            
            logger.info(f"模型加载完成！设备: {self.device}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            self.is_loaded = False
            raise e
    
    def generate_response(self, messages: List[dict], generation_config: dict) -> tuple[str, int]:
        """生成回复内容"""
        if not self.is_loaded:
            raise RuntimeError("模型未加载")
        
        # 应用聊天模板
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        logger.debug(f"格式化后的提示: {formatted_prompt}")
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=Config.MAX_INPUT_LENGTH
        ).to(self.device)
        
        input_tokens = inputs['input_ids'].shape[1]
        logger.info(f"输入token数量: {input_tokens}")
        
        # 生成回复
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **generation_config
            )
        
        # 解码回复（只取新生成的部分）
        response_tokens = outputs[0][input_tokens:]
        response_text = self.tokenizer.decode(response_tokens, skip_special_tokens=True)
        
        # 清理可能的重复或格式问题
        response_text = response_text.strip()
        total_tokens = outputs[0].shape[0]
        
        return response_text, total_tokens

# 初始化模型管理器
model_manager = ModelManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载模型
    try:
        model_manager.load_model()
        logger.info("应用启动完成")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        model_manager.is_loaded = False
    
    yield
    
    # 关闭时清理资源
    if model_manager.model is not None:
        del model_manager.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("模型资源已释放")

# 创建FastAPI应用
app = FastAPI(
    title="角色扮演AI聊天API",
    description="基于Qwen3-8B和LoRA微调的对话API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="根路径")
async def root():
    """服务根路径"""
    return {
        "message": "角色扮演AI聊天API服务运行中",
        "status": "healthy",
        "model_loaded": model_manager.is_loaded,
        "version": "1.0.0"
    }

@app.post("/api/auth/login", response_model=LoginResponse, summary="登录")
async def login(login_request: LoginRequest):
    """登录接口"""
    try:
        logging.info(f"正在登录用户: {login_request.username}")
        user = authenticate_user(login_request.username, login_request.password)
        if not user:
            return LoginResponse(
                success=False,
                message="用户名或密码错误"
            )

        user_info = User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            avatar=user['avatar']
        )
        return LoginResponse(
            success=True,
            user=user_info,
        )
    except Exception as e:
        logging.error(f"登录失败: {str(e)}")
        return LoginResponse(
            success=False,
            message="登录过程中发生错误" 
        )

@app.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """服务健康检查"""
    return HealthResponse(
        status="healthy" if model_manager.is_loaded else "unhealthy",
        model_loaded=model_manager.is_loaded,
        timestamp=datetime.now().isoformat(),
        device=str(model_manager.device) if model_manager.is_loaded else None
    )

@app.post("/chat", response_model=ChatResponse, summary="对话接口")
async def chat_completion(request: ChatRequest):
    """对话生成接口"""
    if not model_manager.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模型未加载完成，请稍后重试"
        )
    
    try:
        # 构建对话历史（限制历史长度）
        recent_messages = request.messages[-Config.MAX_HISTORY_MESSAGES:] 
        if len(request.messages) > Config.MAX_HISTORY_MESSAGES:
            logger.info(f"对话历史截断: {len(request.messages)} -> {len(recent_messages)}")
        
        # 确保有系统提示
        has_system = any(msg.role == "system" for msg in recent_messages)
        if not has_system:
            system_message = ChatMessage(role="system", content=Config.SYSTEM_PROMPT)
            recent_messages = [system_message] + recent_messages
        
        # 转换为字典格式
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in recent_messages]
        
        logger.info(f"处理消息数量: {len(messages_dict)}")
        
        # 生成配置
        generation_config = {
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "do_sample": True,
            "pad_token_id": model_manager.tokenizer.pad_token_id,
            "eos_token_id": model_manager.tokenizer.eos_token_id,
            "repetition_penalty": request.repetition_penalty
        }
        
        # 生成回复
        response_text, total_tokens = model_manager.generate_response(messages_dict, generation_config)
        
        logger.info(f"生成回复长度: {len(response_text)}, 总token数: {total_tokens}")
        
        return ChatResponse(
            role="assistant",
            content=response_text,
            time=datetime.now().strftime("%H:%M"),
            tokens_used=total_tokens
        )
        
    except Exception as e:
        logger.error(f"生成失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失败: {str(e)}"
        )

@app.post("/chat/simple", summary="简化版对话接口")
async def chat_simple(request: SimpleChatRequest):
    """简化版对话接口"""
    if not model_manager.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模型未加载完成"
        )
    
    try:
        # 构建消息
        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": request.message}
        ]
        
        generation_config = {
            "max_new_tokens": request.max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": model_manager.tokenizer.eos_token_id,
            "repetition_penalty": 1.1
        }
        
        response_text, total_tokens = model_manager.generate_response(messages, generation_config)
        
        return {
            "response": response_text,
            "time": datetime.now().strftime("%H:%M"),
            "tokens_used": total_tokens
        }
        
    except Exception as e:
        logger.error(f"简化对话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict

def authenticate_user(username: str, password: str, db=fake_users_db):
    user = get_user(db, username)
    if not user:
        return None
    if user['password'] != password:
        return None
    return user

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level=Config.LOG_LEVEL.lower(),
        reload=False,  # 开发环境启用热重载
    )