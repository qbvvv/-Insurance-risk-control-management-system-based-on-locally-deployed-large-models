"""
保险客户管理模块的简易内存存储（内存版）。

你当前的后端数据库还没全部接入 MySQL，所以先用 Python 列表模拟“customers 表”：
- 每个客户 = 一个 dict（字段值在 dict 里）
- 通过 _next_customer_id 生成内部 id
- 客户编号 customerNo 由 allocate_customer_no() 统一生成：C + 四位年份 + 四位序号（如 C20260001）

如果未来换成 MySQL，只需要把这些 list 操作替换成数据库查询/写入即可。
"""

from datetime import date
from typing import Any, Dict, List, Optional


def allocate_customer_no() -> str:
    """生成新的客户编号，与当年已有编号不重复。"""
    y = date.today().year
    prefix = f"C{y}"
    max_seq = 0
    for c in CUSTOMERS:
        no = (c.get("customerNo") or "").strip()
        if not no.startswith(prefix):
            continue
        tail = no[len(prefix) :]
        if tail.isdigit() and len(tail) == 4:
            max_seq = max(max_seq, int(tail))
    return f"{prefix}{max_seq + 1:04d}"

CUSTOMERS: List[Dict[str, Any]] = [
    {"id": "1", "customerNo": "C20260001", "name": "张伟", "idType": "身份证", "idNo": "110101199001012026", "phone": "13810012026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "北京市朝阳区望京街道", "remark": "线上投保活跃客户", "createdAt": "2026-03-06"},
    {"id": "2", "customerNo": "C20260002", "name": "王晓芳", "idType": "身份证", "idNo": "310101199202142026", "phone": "13910022026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "北京市朝阳区望京街道", "remark": "同址高额保单聚集样本", "createdAt": "2026-03-06"},
    {"id": "3", "customerNo": "C20260003", "name": "李娜", "idType": "身份证", "idNo": "440106198806222026", "phone": "13710032026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "北京市朝阳区望京街道", "remark": "同址高额保单聚集样本", "createdAt": "2026-03-06"},
    {"id": "4", "customerNo": "C20260004", "name": "欧阳子涵", "idType": "身份证", "idNo": "320102198511302026", "phone": "13610042026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "北京市朝阳区望京街道", "remark": "同址高额保单聚集样本", "createdAt": "2026-03-06"},
    {"id": "5", "customerNo": "C20260005", "name": "陈杰", "idType": "身份证", "idNo": "330103199307172026", "phone": "13510052026", "occupation": "办事人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "北京市朝阳区望京街道", "remark": "同址高额保单聚集样本", "createdAt": "2026-03-06"},
    {"id": "6", "customerNo": "C20260006", "name": "杨雨桐", "idType": "身份证", "idNo": "420102199411082026", "phone": "18810062026", "occupation": "生产运输工人", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "北京市朝阳区望京街道", "remark": "同址高额保单聚集样本", "createdAt": "2026-03-06"},
    {"id": "7", "customerNo": "C20260007", "name": "赵磊", "idType": "身份证", "idNo": "510104198912052026", "phone": "18710072026", "occupation": "办事人员", "level": "高风险", "status": "在保", "photo": "", "gender": "男", "address": "四川省成都市锦江区", "remark": "反欺诈规则命中观察", "createdAt": "2026-03-06"},
    {"id": "8", "customerNo": "C20260008", "name": "上官婉儿", "idType": "身份证", "idNo": "120105199605262026", "phone": "18610082026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "天津市河北区", "remark": "家财险和意外险组合", "createdAt": "2026-03-06"},
    {"id": "9", "customerNo": "C20260009", "name": "周强", "idType": "身份证", "idNo": "350203198710192026", "phone": "18510092026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "福建省厦门市思明区", "remark": "线上直销客户", "createdAt": "2026-03-06"},
    {"id": "10", "customerNo": "C20260010", "name": "吴思涵", "idType": "身份证", "idNo": "210102199808032026", "phone": "15610102026", "occupation": "商业服务业人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "辽宁省沈阳市和平区", "remark": "活动期投保客户", "createdAt": "2026-03-06"},
    {"id": "11", "customerNo": "C20260011", "name": "徐鹏", "idType": "身份证", "idNo": "230103198403112026", "phone": "15810112026", "occupation": "国家机关负责人", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "黑龙江省哈尔滨市南岗区", "remark": "长期寿险客户", "createdAt": "2026-03-06"},
    {"id": "12", "customerNo": "C20260012", "name": "孙嘉怡", "idType": "身份证", "idNo": "370102199512242026", "phone": "15910122026", "occupation": "商业服务业人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "山东省济南市历下区", "remark": "商户经营相关保障", "createdAt": "2026-03-06"},
    {"id": "13", "customerNo": "C20260013", "name": "司马明哲", "idType": "身份证", "idNo": "430103198909092026", "phone": "15110132026", "occupation": "生产运输工人", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "湖南省长沙市天心区", "remark": "工伤意外保障需求", "createdAt": "2026-03-06"},
    {"id": "14", "customerNo": "C20260014", "name": "朱琳", "idType": "身份证", "idNo": "610104199001152026", "phone": "15210142026", "occupation": "商业服务业人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "陕西省西安市莲湖区", "remark": "代理人自保单", "createdAt": "2026-03-06"},
    {"id": "15", "customerNo": "C20260015", "name": "高梓轩", "idType": "身份证", "idNo": "500103198706282026", "phone": "15310152026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "重庆市渝中区", "remark": "高端医疗产品需求", "createdAt": "2026-03-06"},
    {"id": "16", "customerNo": "C20260016", "name": "林雪", "idType": "身份证", "idNo": "460106199309212026", "phone": "15510162026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "海南省海口市龙华区", "remark": "门诊医疗责任关注", "createdAt": "2026-03-06"},
    {"id": "17", "customerNo": "C20260017", "name": "何军", "idType": "身份证", "idNo": "341102198802072026", "phone": "15710172026", "occupation": "办事人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "安徽省合肥市蜀山区", "remark": "条款阅读完整", "createdAt": "2026-03-06"},
    {"id": "18", "customerNo": "C20260018", "name": "郭芷若", "idType": "身份证", "idNo": "530103199404132026", "phone": "18210182026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "云南省昆明市盘龙区", "remark": "偏好线上服务", "createdAt": "2026-03-06"},
    {"id": "19", "customerNo": "C20260019", "name": "马超", "idType": "身份证", "idNo": "640104198609162026", "phone": "18310192026", "occupation": "商业服务业人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "宁夏银川市兴庆区", "remark": "渠道佣金核对样本", "createdAt": "2026-03-06"},
    {"id": "20", "customerNo": "C20260020", "name": "罗丹", "idType": "身份证", "idNo": "520103199701272026", "phone": "18410202026", "occupation": "商业服务业人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "贵州省贵阳市云岩区", "remark": "跨地区出险场景", "createdAt": "2026-03-06"},
    {"id": "21", "customerNo": "C20260021", "name": "梁晨曦", "idType": "身份证", "idNo": "450103198312302026", "phone": "18910212026", "occupation": "生产运输工人", "level": "高风险", "status": "在保", "photo": "", "gender": "男", "address": "广西南宁市青秀区", "remark": "车险理赔高频观察", "createdAt": "2026-03-06"},
    {"id": "22", "customerNo": "C20260022", "name": "宋佳", "idType": "身份证", "idNo": "620102199111052026", "phone": "18110222026", "occupation": "办事人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "甘肃省兰州市城关区", "remark": "社区团体投保样本", "createdAt": "2026-03-06"},
    {"id": "23", "customerNo": "C20260023", "name": "诸葛云飞", "idType": "身份证", "idNo": "360102198805142026", "phone": "18010232026", "occupation": "专业技术人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "江西省南昌市东湖区", "remark": "教育行业客户", "createdAt": "2026-03-06"},
    {"id": "24", "customerNo": "C20260024", "name": "谢雨薇", "idType": "身份证", "idNo": "130102199210252026", "phone": "17710242026", "occupation": "办事人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "河北省石家庄市长安区", "remark": "财务报销型客户", "createdAt": "2026-03-06"},
    {"id": "25", "customerNo": "C20260025", "name": "韩天宇", "idType": "身份证", "idNo": "140106198401082026", "phone": "17610252026", "occupation": "办事人员", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "山西省太原市小店区", "remark": "团险配置咨询", "createdAt": "2026-03-06"},
    {"id": "26", "customerNo": "C20260026", "name": "唐蕾", "idType": "身份证", "idNo": "220104199507192026", "phone": "17510262026", "occupation": "农林牧渔水利业", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "吉林省长春市朝阳区", "remark": "农业经营风险保障", "createdAt": "2026-03-06"},
    {"id": "27", "customerNo": "C20260027", "name": "努尔夏提·阿不都热依木", "idType": "身份证", "idNo": "650102199103062026", "phone": "16610272026", "occupation": "生产运输工人", "level": "普通", "status": "在保", "photo": "", "gender": "男", "address": "新疆乌鲁木齐市天山区", "remark": "新疆区域样本客户", "createdAt": "2026-03-06"},
    {"id": "28", "customerNo": "C20260028", "name": "迪丽娜尔·买买提", "idType": "身份证", "idNo": "650104199608112026", "phone": "16610272026", "occupation": "生产运输工人", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "新疆乌鲁木齐市新市区", "remark": "同手机号关联多证件样本", "createdAt": "2026-03-06"},
    {"id": "29", "customerNo": "C20260029", "name": "阿依古丽·吐尔逊", "idType": "身份证", "idNo": "652901199303292026", "phone": "16610272026", "occupation": "商业服务业人员", "level": "普通", "status": "在保", "photo": "", "gender": "女", "address": "新疆阿克苏市", "remark": "同手机号关联多证件样本", "createdAt": "2026-03-06"},
    {"id": "30", "customerNo": "C20260030", "name": "麦尔丹·伊明", "idType": "身份证", "idNo": "653101199012182026", "phone": "16710302026", "occupation": "生产运输工人", "level": "高风险", "status": "在保", "photo": "", "gender": "男", "address": "新疆喀什市", "remark": "高风险客户监控样本", "createdAt": "2026-03-06"},
]

_next_customer_id = 31


def list_customers() -> List[Dict[str, Any]]:
    """返回全部客户（相当于 SELECT * FROM customers）。"""
    return list(CUSTOMERS)


def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """按内部 id 查询客户（相当于 SELECT ... WHERE id = ?）。"""
    for c in CUSTOMERS:
        if c.get("id") == customer_id:
            return c
    return None


def create_customer(data: Dict[str, Any]) -> Dict[str, Any]:
    """新增客户（相当于 INSERT）。customerNo 始终由本模块生成，忽略入参中的编号。"""
    global _next_customer_id
    item = dict(data)
    item.pop("customerNo", None)
    item["customerNo"] = allocate_customer_no()
    item.setdefault("id", str(_next_customer_id))
    item.setdefault("level", "普通")
    item.setdefault("status", "在保")
    item["photo"] = (item.get("photo") or "").strip()[:512]
    item["gender"] = ((item.get("gender") or "未知").strip()[:16] or "未知")
    item["address"] = (item.get("address") or "").strip()[:255]
    item["remark"] = (item.get("remark") or "").strip()[:512]
    item.setdefault("createdAt", date.today().isoformat())
    _next_customer_id += 1
    CUSTOMERS.append(item)
    return item


def update_customer(customer_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新客户字段（相当于 UPDATE ... WHERE id = ?）。不允许修改客户编号。"""
    for idx, c in enumerate(CUSTOMERS):
        if c.get("id") == customer_id:
            patch = dict(data)
            patch.pop("customerNo", None)
            updated = dict(c)
            updated.update(patch)
            updated["id"] = customer_id
            updated["customerNo"] = c.get("customerNo")
            CUSTOMERS[idx] = updated
            return updated
    return None


def delete_customer(customer_id: str) -> bool:
    """删除客户（相当于 DELETE）。"""
    for idx, c in enumerate(CUSTOMERS):
        if c.get("id") == customer_id:
            CUSTOMERS.pop(idx)
            return True
    return False

