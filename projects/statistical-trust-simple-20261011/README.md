# 统计学习与可信决策：完整研究档案

项目身份：`statistical-trust-simple-20261011`。只使用 rsi-simple 0.3.0-simple.9，CPU、项目实验合计 RAM ≤ 8,000,000,000 字节。

## 已保存什么

`LATEST.json` 指向完整的、按 SHA-256 标识的分块 ZIP：60829027 字节，117 个二进制分块，969 个归档条目（968 个 payload 文件和 MANIFEST）。包括全部保留的代码、原始结果、失败、计划、源身份、45 个终结执行回执，以及一致的 SQLite 历史。仅省略可重建 Python 缓存、瞬态监督锁和 SQLite WAL/SHM；隔离依赖环境不属于检查点。

累计真实命令时间：642.4580039849707 秒；24 个已记录研究循环。CREDO 已按证据结束为 inconclusive；当前 active idea 为 PRAXIS `praxis-near-optimal-tree-sets-v1` r1。B047v2 的十组新 bootstrap 尚未运行；原种子、判定标准和内存保护保持不变。没有已验证的新方法。

归档不是新实验，也不等于研究完成。最新科学交接在 ZIP 内的 `START_HERE.md`、`CHECKPOINT.json`、`notes/B048_findings.md`。

## 按需恢复与清理

先读取远端 main 的实际 commit，再只下载本项目目录，保留那个 commit 身份。不要下载其他项目的工作数据：

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/Yunbo-max/cpu.git cpu-restore
cd cpu-restore
git sparse-checkout set projects/statistical-trust-simple-20261011
git rev-parse HEAD
python3 projects/statistical-trust-simple-20261011/checkpoint_io.py verify --repo .
python3 projects/statistical-trust-simple-20261011/checkpoint_io.py restore --repo .
```

恢复器拒绝覆盖已有项目；完整核验各分块、总 ZIP、每个 MANIFEST 文件和 SQLite integrity，再恢复到原绑定路径：
`/workspace/scratch/a5c97e2248bf/statistical_trust_simple`。
不能恢复到原路径时须做静态迁移审查，不盲改旧执行 contract。

恢复后先读原项目 runtime/SKILL.md、Simple 引用和状态/inbox/alerts/health；核对源 digest 与全部任务身份。原空闲监督器已从精确执行会话退出（exit 130），这不是用户停止研究。只在资源和执行窗口允许时重启同一 runner；不要 init、重置累计消耗或把等待说成科研。必要时按保留的安装回执重建隔离 PRAXIS 环境。

每批结果完成后，在无活跃/未知任务、监督锁已释放的边界：

1. 更新真实结果、失败、解释、下一步和 CHECKPOINT；用原 `scripts/package_checkpoint.py` 生成一致快照。
2. 通过已授权 GitHub 连接上传不可变分块及索引。普通 git push 若没有凭据则不提取其他工具凭据；使用连接器。当前分块为 512 KiB、base64 blob API 写入。
3. 以最新 main tree 为基础，只更新本目录；用 expected-head 保护发布，禁止强推。保留旧归档和失败，不覆盖其他项目。
4. 从发布的精确 commit 重新下载并运行 verify。只在成功后执行 cleanup。

```bash
python3 projects/statistical-trust-simple-20261011/checkpoint_io.py cleanup --repo .
python3 projects/statistical-trust-simple-20261011/checkpoint_io.py cleanup --repo . --apply
```

cleanup 先取得本项目监督锁、检查所有任务终结、比对本地每个历史文件与远端快照，任何更新/未归档文件都会拒绝删除。它只删除这个明确项目根下已核验的文件，保留研究在 GitHub 的恢复能力。外层下载目录/临时 ZIP 也只有验证后才按准确路径清理；保持一个小型恢复指针即可。上传或验证失败时保留本地原件。

文件占用与 RAM 不等价：删除归档副本不能保证立即释放共享宿主的文件缓存，更不能清理其他项目的进程。禁止全局 drop_caches 或终止其他项目。

本仓库为用户指定的公开目的地。不要上传凭据、私钥或账户缓存。第三方代码、论文和数据保留原作者身份及许可证；本项目不为第三方材料另授许可证。

发布后的实际远端读回及本地清理结果见 `MIGRATION_RECEIPT.json`（尚未出现时不可推断已清理）。
