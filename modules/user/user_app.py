"""
用户应用服务层
"""
from typing import Optional, List
from datetime import datetime
from common.repository import get_repository
from common.enums import UserType, UserStatus
from .user_schema import User, UserCreateRequest


class UserApp:
    """用户应用服务"""
    
    def __init__(self):
        self.repo = get_repository()
        self.table_name = "user"
    
    def _generate_id(self) -> str:
        """生成用户ID"""
        import uuid
        return f"USER_{uuid.uuid4().hex[:16]}"
    
    def create_user(self, request: UserCreateRequest) -> User:
        """创建用户"""
        user_id = self._generate_id()
        now = datetime.now()
        
        # 处理user_type，可能是枚举或字符串
        user_type_value = request.user_type.value if hasattr(request.user_type, 'value') else request.user_type
        
        user_data = {
            'id': user_id,
            'user_id': user_id,
            'user_name': request.user_name,
            'user_type': user_type_value,
            'user_status': UserStatus.ACTIVE.value,
            'identity_no': request.identity_no,
            'phone': request.phone,
            'email': request.email,
            'create_time': now,
            'update_time': now
        }
        
        self.repo.create(self.table_name, user_data)
        
        # 初始化用户余额
        from modules.user_asset.user_asset_app import UserAssetApp
        asset_app = UserAssetApp()
        asset_app.init_user_balance(user_id)
        
        return User(**user_data)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        user_data = self.repo.get(self.table_name, user_id)
        if user_data:
            return User(**user_data)
        return None
    
    def list_users(self, filters: Optional[dict] = None) -> List[User]:
        """列出用户"""
        users_data = self.repo.list(self.table_name, filters)
        return [User(**data) for data in users_data]
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """更新用户"""
        kwargs['update_time'] = datetime.now()
        user_data = self.repo.update(self.table_name, user_id, kwargs)
        if user_data:
            return User(**user_data)
        return None

