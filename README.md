# Study-Abroad-Application-Helper-LLM
基于pyqt与deepseek的留学文书助手，用户可根据引导来填写自己的实际情况来生成个性化的文书。

*目前为原始简陋版本，暂未维护，生成文书需要仔细修改。*
### 运行
使用的python版本3.9，
运行
`pip install -r requirements.txt`
安装依赖.


使用前需要在[deepseek api开放平台](https://platform.deepseek.com/usage)
注册获取自己的api-keys,填写到该应用的对应位置。





生成的文件存放于./output/

如果需要通过应用本地编译.tex文件需安装
[MiKTeX](https://miktex.org/download)并配置环境变量。

建议将生成的.tex文件以及照片上传至[overleaf](https://cn.overleaf.com/)，使用overleaf在线环境进行编译修改。

### 注意

1. 您填写的个人信息会被上传至deepseek服务器在线分析，请不要填写敏感信息。

2. 内容为大语言模型根据用户填写的信息生成，与作者无关，不能保证生成内容的真实性，请不要直接使用于求职、留学申请。

3. 本项目为作者作业练习项目，不涉及盈利。


