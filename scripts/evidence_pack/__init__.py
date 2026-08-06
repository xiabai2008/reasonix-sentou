# -*- coding: utf-8 -*-
"""
DawnForge 证据包模块 (evidence_pack)

对标 VulnClaw 的"证据强制"机制，将反幻觉从模型自觉升级为代码硬约束。

模块:
    evidence_harvest    证据采集: 分配 EVID 编号 + 逐字符归属校验
    memory_archive      记忆归档: 高信号证据去重沉淀到经验/攻击链
    report_pack         报告打包: 生成带 [EVID-0NN] 的可复核报告

作者: DawnForge 破晓
"""

__version__ = "1.0.0"