-- ============================================
-- 基金交易系统数据库建表语句
-- ============================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `user_id` VARCHAR(32) PRIMARY KEY COMMENT '用户ID，全局唯一',
    `user_name` VARCHAR(50) COMMENT '用户姓名',
    `user_type` VARCHAR(20) NOT NULL DEFAULT 'PERSONAL' COMMENT '用户类型：PERSONAL/INSTITUTION',
    `user_status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '用户状态：ACTIVE/INACTIVE/FROZEN',
    `identity_no` VARCHAR(30) COMMENT '身份证/机构代码',
    `phone` VARCHAR(20) COMMENT '手机号',
    `email` VARCHAR(100) COMMENT '邮箱',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_status` (`user_status`),
    INDEX `idx_user_type` (`user_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 用户银行卡表
CREATE TABLE IF NOT EXISTS `user_bank_card` (
    `card_id` VARCHAR(32) PRIMARY KEY COMMENT '银行卡ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID，关联user.user_id',
    `bank_code` VARCHAR(20) NOT NULL COMMENT '银行代码',
    `bank_name` VARCHAR(50) COMMENT '银行名称',
    `card_no` VARCHAR(30) NOT NULL COMMENT '银行卡号（加密存储）',
    `card_type` VARCHAR(20) NOT NULL DEFAULT 'DEBIT' COMMENT '卡类型：DEBIT/CREDIT',
    `card_status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE/INACTIVE/FROZEN',
    `bind_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',
    `is_default` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否默认卡',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    INDEX `idx_user_card` (`user_id`, `card_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户银行卡表';

-- 3. 用户资金余额表
CREATE TABLE IF NOT EXISTS `user_balance` (
    `balance_id` VARCHAR(32) PRIMARY KEY COMMENT '余额ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID，关联user.user_id',
    `available_balance` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '可用余额',
    `frozen_balance` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '冻结余额',
    `total_balance` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '总余额（计算字段）',
    `last_update` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    UNIQUE KEY `uk_user_balance` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户资金余额表';

-- 4. 资金变动委托表
CREATE TABLE IF NOT EXISTS `capital_change_entrust` (
    `entrust_id` VARCHAR(32) PRIMARY KEY COMMENT '委托ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
    `card_id` VARCHAR(32) NOT NULL COMMENT '银行卡ID',
    `change_type` VARCHAR(20) NOT NULL COMMENT '变动类型：IN/OUT',
    `amount` DECIMAL(18,4) NOT NULL COMMENT '变动金额',
    `third_party_no` VARCHAR(50) COMMENT '第三方流水号',
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态：PENDING/PROCESSING/SUCCESS/FAILED',
    `request_data` JSON COMMENT '请求数据',
    `response_data` JSON COMMENT '响应数据',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `process_time` DATETIME COMMENT '处理时间',
    `complete_time` DATETIME COMMENT '完成时间',
    `error_msg` TEXT COMMENT '错误信息',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    FOREIGN KEY (`card_id`) REFERENCES `user_bank_card`(`card_id`),
    INDEX `idx_user_status` (`user_id`, `status`),
    INDEX `idx_change_type` (`change_type`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资金变动委托表';

-- 5. 资金清算表
CREATE TABLE IF NOT EXISTS `capital_settlement` (
    `settlement_id` VARCHAR(32) PRIMARY KEY COMMENT '清算ID',
    `entrust_id` VARCHAR(32) NOT NULL COMMENT '委托ID，关联capital_change_entrust.entrust_id',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
    `balance_id` VARCHAR(32) NOT NULL COMMENT '余额ID',
    `settlement_type` VARCHAR(20) NOT NULL COMMENT '清算类型：CAPITAL_IN/CAPITAL_OUT',
    `amount` DECIMAL(18,4) NOT NULL COMMENT '清算金额',
    `result_status` VARCHAR(20) NOT NULL COMMENT '结果状态：SUCCESS/FAILED',
    `settlement_data` JSON COMMENT '清算数据',
    `settlement_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '清算时间',
    `remark` VARCHAR(500) COMMENT '备注',
    FOREIGN KEY (`entrust_id`) REFERENCES `capital_change_entrust`(`entrust_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    FOREIGN KEY (`balance_id`) REFERENCES `user_balance`(`balance_id`),
    INDEX `idx_entrust_settlement` (`entrust_id`),
    INDEX `idx_user_settlement` (`user_id`, `settlement_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资金清算表';

-- 6. 基金账户表
CREATE TABLE IF NOT EXISTS `fund_account` (
    `fund_account_id` VARCHAR(32) PRIMARY KEY COMMENT '基金账户ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID，关联user.user_id',
    `account_no` VARCHAR(30) NOT NULL COMMENT '基金账户号',
    `account_type` VARCHAR(20) NOT NULL DEFAULT 'INDIVIDUAL' COMMENT '账户类型：INDIVIDUAL/INSTITUTION',
    `account_status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE/INACTIVE/FROZEN',
    `open_date` DATE NOT NULL COMMENT '开户日期',
    `close_date` DATE COMMENT '销户日期',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    INDEX `idx_user_account` (`user_id`, `account_status`),
    UNIQUE KEY `uk_account_no` (`account_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金账户表';

-- 7. 基金账户委托表
CREATE TABLE IF NOT EXISTS `fund_account_entrust` (
    `entrust_id` VARCHAR(32) PRIMARY KEY COMMENT '委托ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
    `account_type` VARCHAR(20) NOT NULL DEFAULT 'INDIVIDUAL' COMMENT '账户类型',
    `source_channel` VARCHAR(30) NOT NULL DEFAULT 'WEB' COMMENT '来源渠道：WEB/APP/BANK',
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态：PENDING/PROCESSING/SUCCESS/FAILED',
    `request_data` JSON COMMENT '请求数据',
    `response_data` JSON COMMENT '响应数据',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `process_time` DATETIME COMMENT '处理时间',
    `complete_time` DATETIME COMMENT '完成时间',
    `error_msg` TEXT COMMENT '错误信息',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    INDEX `idx_user_status` (`user_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金账户委托表';

-- 8. 基金产品表
CREATE TABLE IF NOT EXISTS `fund_product` (
    `product_id` VARCHAR(32) PRIMARY KEY COMMENT '产品ID',
    `product_code` VARCHAR(20) NOT NULL COMMENT '产品代码',
    `product_name` VARCHAR(100) NOT NULL COMMENT '产品名称',
    `product_type` VARCHAR(20) NOT NULL DEFAULT 'EQUITY' COMMENT '产品类型：EQUITY/BOND/MIXED/MONETARY',
    `product_status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE/INACTIVE',
    `risk_level` VARCHAR(10) NOT NULL DEFAULT 'R3' COMMENT '风险等级：R1-R5',
    `fund_company` VARCHAR(50) COMMENT '基金公司',
    `issue_date` DATE NOT NULL COMMENT '发行日期',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_product_type_status` (`product_type`, `product_status`),
    UNIQUE KEY `uk_product_code` (`product_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金产品表';

-- 9. 基金单位净值表
CREATE TABLE IF NOT EXISTS `fund_net_value` (
    `nav_id` VARCHAR(32) PRIMARY KEY COMMENT '净值ID',
    `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID，关联fund_product.product_id',
    `net_value` DECIMAL(10,4) NOT NULL COMMENT '单位净值',
    `accumulated_nav` DECIMAL(10,4) COMMENT '累计净值',
    `nav_date` DATE NOT NULL COMMENT '净值日期',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`product_id`) REFERENCES `fund_product`(`product_id`),
    INDEX `idx_product_date` (`product_id`, `nav_date`),
    UNIQUE KEY `uk_product_nav_date` (`product_id`, `nav_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金单位净值表';

-- 10. 基金交易委托表
CREATE TABLE IF NOT EXISTS `fund_transaction_entrust` (
    `entrust_id` VARCHAR(32) PRIMARY KEY COMMENT '委托ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
    `fund_account_id` VARCHAR(32) NOT NULL COMMENT '基金账户ID，关联fund_account.fund_account_id',
    `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID，关联fund_product.product_id',
    `transaction_type` VARCHAR(20) NOT NULL COMMENT '交易类型：SUBSCRIBE/REDEEM',
    `amount` DECIMAL(18,4) COMMENT '交易金额（申购用）',
    `share` DECIMAL(18,4) COMMENT '交易份额（赎回用）',
    `nav` DECIMAL(10,4) COMMENT '交易净值',
    `fee` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '手续费',
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态：PENDING/PROCESSING/SUCCESS/FAILED',
    `request_data` JSON COMMENT '请求数据',
    `response_data` JSON COMMENT '响应数据',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `process_time` DATETIME COMMENT '处理时间',
    `complete_time` DATETIME COMMENT '完成时间',
    `error_msg` TEXT COMMENT '错误信息',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    FOREIGN KEY (`fund_account_id`) REFERENCES `fund_account`(`fund_account_id`),
    FOREIGN KEY (`product_id`) REFERENCES `fund_product`(`product_id`),
    INDEX `idx_user_status` (`user_id`, `status`),
    INDEX `idx_account_product` (`fund_account_id`, `product_id`),
    INDEX `idx_transaction_type` (`transaction_type`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金交易委托表';

-- 11. 交易确认表
CREATE TABLE IF NOT EXISTS `fund_transaction_confirm` (
    `confirm_id` VARCHAR(32) PRIMARY KEY COMMENT '确认ID',
    `entrust_id` VARCHAR(32) NOT NULL COMMENT '委托ID，关联fund_transaction_entrust.entrust_id',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
    `fund_account_id` VARCHAR(32) NOT NULL COMMENT '基金账户ID',
    `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID',
    `confirm_type` VARCHAR(20) NOT NULL COMMENT '确认类型：SUBSCRIBE/REDEEM',
    `result_status` VARCHAR(20) NOT NULL COMMENT '结果状态：SUCCESS/FAILED',
    `confirm_data` JSON COMMENT '确认数据',
    `confirm_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '确认时间',
    `remark` VARCHAR(500) COMMENT '备注',
    FOREIGN KEY (`entrust_id`) REFERENCES `fund_transaction_entrust`(`entrust_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    FOREIGN KEY (`fund_account_id`) REFERENCES `fund_account`(`fund_account_id`),
    FOREIGN KEY (`product_id`) REFERENCES `fund_product`(`product_id`),
    INDEX `idx_entrust_confirm` (`entrust_id`),
    INDEX `idx_user_confirm` (`user_id`, `confirm_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易确认表';

-- 12. 基金份额表
CREATE TABLE IF NOT EXISTS `fund_share` (
    `share_id` VARCHAR(32) PRIMARY KEY COMMENT '份额ID',
    `fund_account_id` VARCHAR(32) NOT NULL COMMENT '基金账户ID，关联fund_account.fund_account_id',
    `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID，关联fund_product.product_id',
    `total_share` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '总份额',
    `available_share` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '可用份额',
    `frozen_share` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '冻结份额',
    `last_update` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (`fund_account_id`) REFERENCES `fund_account`(`fund_account_id`),
    FOREIGN KEY (`product_id`) REFERENCES `fund_product`(`product_id`),
    UNIQUE KEY `uk_account_product` (`fund_account_id`, `product_id`),
    INDEX `idx_account_share` (`fund_account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金份额表';

-- 13. 用户总资产表
CREATE TABLE IF NOT EXISTS `user_total_asset` (
    `asset_id` VARCHAR(32) PRIMARY KEY COMMENT '资产ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID，关联user.user_id',
    `total_asset` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '总资产',
    `total_fund_asset` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '基金总资产',
    `total_balance` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '总余额',
    `calc_date` DATE NOT NULL COMMENT '计算日期',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    INDEX `idx_user_date` (`user_id`, `calc_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户总资产表';

-- 14. 用户基金资产表
CREATE TABLE IF NOT EXISTS `user_fund_asset` (
    `fund_asset_id` VARCHAR(32) PRIMARY KEY COMMENT '基金资产ID',
    `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID，关联user.user_id',
    `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID，关联fund_product.product_id',
    `fund_share` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '持有份额',
    `fund_value` DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '基金价值',
    `nav` DECIMAL(10,4) NOT NULL COMMENT '计算净值',
    `calc_date` DATE NOT NULL COMMENT '计算日期',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    FOREIGN KEY (`product_id`) REFERENCES `fund_product`(`product_id`),
    INDEX `idx_user_product` (`user_id`, `product_id`),
    INDEX `idx_user_date` (`user_id`, `calc_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户基金资产表';

