# Task: Debug MCP 502 and 400 Errors

- [x] 解决 MCP Server 的 502 Bad Gateway 错误 (通过切换到 stdio transport 绕过网络代理干扰) <!-- id: 0 -->
- [x] 解决 HeyGen 原生工具的 400 Bad Request 错误 (使用官方 SDK 重新封装) <!-- id: 1 -->
- [x] 解决 Stdio 模式下的 "Script not found: -u" 错误 (优化路径解析与命令行构建) <!-- id: 6 -->
- [x] 整合视频生成工具，通过 stdio 支持本地运行 <!-- id: 2 -->
- [/] 验证端到端功能 <!-- id: 3 -->
    - [x] 重启服务并配置 stdio <!-- id: 4 -->
    - [/] 运行模拟测试 <!-- id: 5 -->
