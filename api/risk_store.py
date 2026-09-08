"""
风控与规则管理模块的简易内存存储（内存版）。

为什么需要它？
- 前端需要一个“能跑起来”的黑名单/预警数据接口
- 但你当前还没有接入数据库，所以这里先用 Python 列表模拟“表”

后续如果换成 MySQL：
- 这里的 list/add 函数会被数据库查询/写入替代
"""

from typing import Any, Dict, List

# 黑名单演示种子（姓名/证件号与客户种子 customer_store 一致，便于演示「客户↔风控」闭环）
BLACKLIST_SEED: List[Dict[str, str]] = [
    {"name": "梁晨曦", "idNo": "450103198312302026", "reason": "近12个月疑似异常高频理赔（车险观察）", "status": "启用"},
    {"name": "麦尔丹·伊明", "idNo": "653101199012182026", "reason": "同设备多账号短期密集投保", "status": "启用"},
    {"name": "赵磊", "idNo": "510104198912052026", "reason": "客户等级为高风险，反欺诈规则命中复核", "status": "启用"},
    {"name": "王晓芳", "idNo": "310101199202142026", "reason": "同址高额保单聚集，疑似集中投保", "status": "启用"},
    {"name": "迪丽娜尔·买买提", "idNo": "650104199608112026", "reason": "同手机号关联多证件，需来源复核", "status": "启用"},
]

# 黑名单“表”（内存里的一行数据 = 一个 dict）
BLACKLIST: List[Dict[str, Any]] = [
    {"id": str(i + 1), **dict(row)} for i, row in enumerate(BLACKLIST_SEED)
]

# 风险预警种子（与 MySQL 空表播种一致）；内存表由下方生成带 id 的 ALERTS
RISK_ALERT_SEED: List[Dict[str, str]] = [
    {"code": "AL2026030601", "type": "集中投保", "desc": "短期内同一地址多笔高保额投保", "level": "高"},
    {"code": "AL2026030602", "type": "异常理赔", "desc": "同一客户近30天理赔金额显著高于历史均值", "level": "高"},
    {"code": "AL2026030603", "type": "证件异常", "desc": "批量证件末位规律一致，需复核来源真实性", "level": "中"},
    {"code": "AL2026030604", "type": "夜间理赔", "desc": "凌晨时段多笔高额理赔集中发生", "level": "高"},
    {"code": "AL2026030605", "type": "渠道异动", "desc": "单渠道7日内新单量环比异常攀升", "level": "中"},
    {"code": "AL2026030606", "type": "收款风险", "desc": "同一收款账户短期承接多客户赔款入账", "level": "高"},
    {"code": "AL2026030607", "type": "代理人风险", "desc": "单代理人名下短期出险率显著高于渠道均值", "level": "中"},
    {"code": "AL2026030608", "type": "退保重投", "desc": "续保窗口外同一客户频繁退保重投", "level": "中"},
    {"code": "AL2026030609", "type": "设备伪冒", "desc": "同一设备指纹24小时内关联多证件投保", "level": "高"},
    {"code": "AL2026030610", "type": "关系网络", "desc": "与欺诈名单客户在地址或收款卡上多项重合", "level": "高"},
    {"code": "AL2026030611", "type": "保单早赔", "desc": "起保72小时内高额理赔案件集中出现", "level": "高"},
    {"code": "AL2026030612", "type": "团单异常", "desc": "团单被保人数与工商登记雇员数偏离过大", "level": "低"},
]

# 风险预警“表”
# - id：内部唯一编号
# - code：预警编号（如 AL2026....）
# - type/desc：预警类型与说明
# - level：风险等级
ALERTS: List[Dict[str, Any]] = [
    {"id": str(i + 1), **row} for i, row in enumerate(RISK_ALERT_SEED)
]

_next_blacklist_id = len(BLACKLIST) + 1
_next_alert_id = len(ALERTS) + 1


def list_blacklist() -> List[Dict[str, Any]]:
    """读取整张黑名单表。"""
    return list(BLACKLIST)  # 返回副本，避免调用方误改原列表


def add_blacklist(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    新增一条黑名单记录。

    由于是内存存储，这里用 _next_blacklist_id 自动生成 id。
    """
    global _next_blacklist_id
    item = dict(item)
    item.setdefault("id", str(_next_blacklist_id))
    item.setdefault("status", "启用")
    _next_blacklist_id += 1
    BLACKLIST.append(item)
    return item


def update_blacklist(item_id: str, data: Dict[str, Any]) -> Dict[str, Any] | None:
    """按 id 更新黑名单记录。"""
    for i, x in enumerate(BLACKLIST):
        if str(x.get("id")) == str(item_id):
            row = dict(x)
            row.update({k: v for k, v in dict(data).items() if v is not None})
            row["id"] = str(item_id)
            BLACKLIST[i] = row
            return row
    return None


def delete_blacklist(item_id: str) -> bool:
    """按 id 删除黑名单记录。"""
    for i, x in enumerate(BLACKLIST):
        if str(x.get("id")) == str(item_id):
            BLACKLIST.pop(i)
            return True
    return False


def list_alerts() -> List[Dict[str, Any]]:
    """读取整张风险预警表。"""
    return list(ALERTS)


def add_alert(item: Dict[str, Any]) -> Dict[str, Any]:
    """新增一条风险预警记录（同样使用内存自增 id）。"""
    global _next_alert_id
    item = dict(item)
    item.setdefault("id", str(_next_alert_id))
    item.setdefault("code", f"AL{_next_alert_id:08d}")
    _next_alert_id += 1
    ALERTS.append(item)
    return item
