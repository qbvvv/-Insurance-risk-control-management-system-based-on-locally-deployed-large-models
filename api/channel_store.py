"""
销售渠道主数据 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

CHANNELS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "channelCode": "AG001",
        "channelName": "个人代理渠道",
        "channelType": "代理人",
        "manager": "张主管",
        "commissionRule": "首年 25%，续期 5%",
        "contactPhone": "021-68551001",
        "status": "合作中",
        "remark": "",
        "createdAt": "2026-03-01",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "channelCode": "BN001",
        "channelName": "XX 银行保险部",
        "channelType": "银行",
        "manager": "李经理",
        "commissionRule": "首年 15%，续期 3%",
        "contactPhone": "010-65232002",
        "status": "合作中",
        "remark": "",
        "createdAt": "2026-03-01",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "3",
        "channelCode": "BR001",
        "channelName": "XX 保险经纪公司",
        "channelType": "经纪",
        "manager": "刘总监",
        "commissionRule": "首年 12%，续期 2.5%",
        "contactPhone": "021-58881200",
        "status": "合作中",
        "remark": "经代协议 2026 版",
        "createdAt": "2026-02-15",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "4",
        "channelCode": "WS001",
        "channelName": "网销直营旗舰店",
        "channelType": "网销",
        "manager": "陈运营",
        "commissionRule": "按 CPA 结算，单笔 80–200 元",
        "contactPhone": "400-800-9001",
        "status": "合作中",
        "remark": "信息流投放渠道",
        "createdAt": "2026-01-10",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "5",
        "channelCode": "TM001",
        "channelName": "电话销售中心",
        "channelType": "电销",
        "manager": "马经理",
        "commissionRule": "坐席绩效制，首单阶梯奖励",
        "contactPhone": "0755-26600001",
        "status": "合作中",
        "remark": "",
        "createdAt": "2025-12-01",
        "updatedAt": "2026-03-07",
    },
    {
        "id": "6",
        "channelCode": "YL001",
        "channelName": "异业合作-XX出行",
        "channelType": "异业",
        "manager": "何商务",
        "commissionRule": "联合会员权益兑换，按激活量结算",
        "contactPhone": "010-90001122",
        "status": "暂停",
        "remark": "季度复盘后恢复",
        "createdAt": "2025-11-20",
        "updatedAt": "2026-03-08",
    },
]

_next_id = 7


def allocate_channel_code() -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"CH{d}"
    n = sum(1 for c in CHANNELS if str(c.get("channelCode", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def list_channels() -> List[Dict[str, Any]]:
    return list(CHANNELS)


def get_channel(channel_id: str) -> Optional[Dict[str, Any]]:
    for c in CHANNELS:
        if c.get("id") == channel_id:
            return c
    return None


def create_channel(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_id
    item = dict(data)
    item.setdefault("id", str(_next_id))
    cc = (item.get("channelCode") or "").strip()
    if not cc:
        item["channelCode"] = allocate_channel_code()
    else:
        item["channelCode"] = cc
    item.setdefault("manager", "")
    item.setdefault("commissionRule", "")
    item.setdefault("contactPhone", "")
    item.setdefault("status", "合作中")
    item.setdefault("remark", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_id += 1
    CHANNELS.append(item)
    return item


def update_channel(channel_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, c in enumerate(CHANNELS):
        if c.get("id") == channel_id:
            updated = dict(c)
            updated.update(data)
            updated["id"] = channel_id
            updated["updatedAt"] = date.today().isoformat()
            CHANNELS[idx] = updated
            return updated
    return None


def delete_channel(channel_id: str) -> bool:
    for idx, c in enumerate(CHANNELS):
        if c.get("id") == channel_id:
            CHANNELS.pop(idx)
            return True
    return False
