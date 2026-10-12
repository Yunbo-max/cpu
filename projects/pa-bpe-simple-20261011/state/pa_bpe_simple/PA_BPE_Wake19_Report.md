# PA-BPE wake19 机制审计

本轮回答一个开发集机制问题：固定hybrid为何能在两个已暴露确认域形成比full parity arms更稳健的公平—成本折中。没有训练新方法，也没有再次打开或调整GlobalVoices/FLORES结果。

## 方法与核验

- 输入：固定Classical、hybrid、base各1000 merges；每语100000预分词训练字典；970条内容对齐TICO英/法/西开发句。
- 逐merge精确应用non-overlap规则，记录训练/开发的逐语言边际token降幅、当前最高成本语言、effect owner、Gini变化和pair-gap符号翻转。
- Python独立重建`Whitespace + ByteLevel(add_prefix_space=true,use_regex=false)`；rank1000三臂逐语言均值与旧tokenizers 0.22.1结果精确一致。
- 主核验36项、解释核验16项全部PASS。

## 新结果

hybrid与Classical前500 merges完全相同。共同rank500开发均值为英65.9289、法78.7649、西76.6443，Gini 0.0386621。

hybrid尾部选中法语323次、西语177次、英语0次；428/500次selector也是实际开发降幅最大的语言，487/500次selector获得正降幅。相对Classical尾部，hybrid的token降幅差为英-4836、法+2305、西-633，净-3164。这把更多容量给法语，但以较少总体压缩为代价。

hybrid尾部把Gini降低0.0211368，Classical尾部反而提高0.00435336。与此同时，局部平滑假设失败：hybrid和base尾部均有208次精确符号翻转；hybrid全部为法西差距翻转，首次rank528、末次rank995，翻转后绝对差中位数23 tokens。hybrid目标切换222次，base为215次。

因此机制结论被修订为：全局前缀提供高效共享压缩，随后有限长度的parity控制重分配收益；hybrid并未让反应式控制器自身更平滑。它限制了控制器介入的时长，而不是消除了近零差距处的追逐。

## 资源、异常与边界

四个attempt均成功，计费wall 100.866952147秒，最高RSS 52,617,216字节；无OOM、timeout或等待。一次重复runner启动被既有锁安全拒绝，未重复运行科学任务；管理探针出现一次宿主loader异常，降级到runner health并核对全部任务终态。

这些数据全部属于已暴露TICO开发范围，能解释固定代码路径，不能证明确认域的因果机制或方法新颖性。下一候选必须先在开发集运行，之后才可另找未曝光确认域。
