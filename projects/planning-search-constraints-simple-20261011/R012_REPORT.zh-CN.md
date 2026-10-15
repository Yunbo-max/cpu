# R012：作者实际强配置的边界与原生可行性

固定Simple13、原作者c4d2c76、CPU-only/thread1、唯一队列，未重跑R010/R011已完成样本。

本次取得Zenodo17515416实际源码/脚本包，发布MD5及SHA256一致；746个源码文件逐个与当前820文件作者pin匹配，74个缺项是工作流/测试/发布辅助文件，没有改源或升级。四脚本静态展开50行配置；不import或运行下载脚本。独立原文核对和协调者源核对均表明：归档additive配方不是网页projection+三Cartesian命令；脚本的other_scp_online_opts仅定义未使用，实际沿用all/200s等源默认。

论文多抽象最强总体配置是regression operators-only（Do），不是states_ops；总体覆盖优势不保证每个domain/task更强。实际配方使用随机排序landmarks(combine_facts=false)+goals、onlineSCP和dead-pair pruning，900s/1M是共享构建边界。旧报道baseline数据的生成脚本未随此脚本包提供，精确C458运行命令仍欠原始属性证据。

## 会改变下一决策的源语义结果

Do没有abstract_space_disambiguation参数，固定源默认none()。其两个disambiguate重载都返回false；ordinary exact-U唯一17行diff完全位于disambiguated_v1||disambiguated_v2的真分支。因此本exact配方不会进入改动分支，沿用原else={splitvar}。这是条件源语义边界，不是两个linkedbinary计时差必为零的测量，不把之前states_ops收益推广到Do。

## 真正原生执行

新officialtask `R012-BWp06-author-additive-ops-feasibility-W5-v1` 实际包含原版preprocess-h2和原版additiveDo两串行阶段，两项exit0。h2输出SAS22645B/SHA2227d8337176dae2867255cef3a2458621cfeeb7acf6ad5c3a86bc6939686fcd，区别于原R011未h2的SAS，不能混算速度比。求解实际28个Cartesian组件、33061状态、1000002非自环；1M检查可按整次refine超出，这里保留真实1000002。expanded9830440/evaluated17639567；计划长度26/cost26，原始p06 PDDL独立VAL有效，未抄旧单抽象work/plan。

直接native wait4 user+system：h2 10905us，作者求解92205939us；求解wall92.222328s、native maxRSS717451264B。原作者内部构建wall3.147884s、search wall89.015953s仅作描述，不分解为谓词CPU。无新增observer/profiler，源码/binary身份与argv、两级guard、原始日志/usage/VAL均绑定。

每native仍120CPU/2500M_AS/145wall/2.8GBgroupRSS/thread1/affinity0，整体仅kernel8GiB；这是明确缩减边界的单个暴露任务可行性，不是论文1800s/8GiB全覆盖复现、规划最优性证明、每组件图等价或候选速度/新颖性结果。强作者实际可运行，不能把它的不同运行时直接归咎于宿主CPU不足。

## 工程与下一步

只读恢复v1遇到可选memory.pressure文件缺失，v2保留missing状态后成功；两次selector预检查分别拒绝不支持entry及未选解释/contrast、错误status枚举，v3两接口gaps=[]后才派发。均发生native前，原文件/日志保留，不算新增原生失败或周期。原监督进程同boot确实不存在且34terminal0reserve后才同W5恢复，不改SQLite/旧stop/deadline。

不为inactive branch再开patched-vs-author计时网格。下一步应基于此真实强配置的工作分布选择新可证伪瓶颈或限定state-heavy方法/质量比较，必要时先实现完整instance-safe组件见证；保留closest-primary/真正跨domain条件/完整失败分母债。不无限升配Depots、不挑有利重复。源码/当前控制/unique/.o不删，所有历史包/坏库forensics保留。
