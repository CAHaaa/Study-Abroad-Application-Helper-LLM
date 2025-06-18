import os
import sys
import datetime
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QFileDialog, QGroupBox,
    QProgressBar, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pylatex import Document, Section, Subsection, Command, Figure
from pylatex.utils import NoEscape

# 确保输出目录存在
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


class DeepSeekAPIWorker(QThread):
    """后台线程处理DeepSeek API调用"""
    finished = pyqtSignal(str, bool)  # (生成内容, 是否成功)
    progress = pyqtSignal(int)  # 进度百分比

    def __init__(self, api_key, prompt, model="deepseek-chat", parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.prompt = prompt
        self.model = model
        self.url = "https://api.deepseek.com/v1/chat/completions"

    def run(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [
                    {"role": "system",
                     "content": "你是一位专业的留学求职文书助手，根据用户提供的信息生成高质量的个性化文书。"},
                    {"role": "user", "content": self.prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False
            }

            self.progress.emit(30)
            response = requests.post(self.url, headers=headers, json=data, timeout=120)
            self.progress.emit(70)

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                self.progress.emit(100)
                self.finished.emit(content, True)
            else:
                error_msg = f"API错误: {response.status_code}\n{response.text}"
                self.finished.emit(error_msg, False)

        except Exception as e:
            self.finished.emit(f"请求异常: {str(e)}", False)


class ResumeGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("留学求职文书助手 - DeepSeek集成版")
        self.setGeometry(100, 100, 900, 700)

        # 主控件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 创建表单区域
        self.create_api_group(main_layout)
        self.create_personal_info_group(main_layout)
        self.create_academic_group(main_layout)
        self.create_target_group(main_layout)
        self.create_action_buttons(main_layout)
        self.create_progress_bar(main_layout)

        # 初始化数据
        self.api_key = ""
        self.photo_path = ""
        self.generated_content = ""
        self.generated_tex_path = ""

    def create_api_group(self, layout):
        group = QGroupBox("DeepSeek API 设置")
        form = QFormLayout()

        # API 密钥输入
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("输入DeepSeek API密钥 (sk-...)")
        self.api_input.setEchoMode(QLineEdit.Password)
        form.addRow(QLabel("API密钥:"), self.api_input)

        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems(["deepseek-chat (V3通用模型)", "deepseek-reasoner (R1推理模型)"])
        form.addRow(QLabel("模型选择:"), self.model_combo)

        group.setLayout(form)
        layout.addWidget(group)

    def create_personal_info_group(self, layout):
        group = QGroupBox("个人信息")
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.photo_button = QPushButton("选择照片")
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(100, 100)
        self.photo_preview.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setText("无照片")

        photo_layout = QHBoxLayout()
        photo_layout.addWidget(self.photo_button)
        photo_layout.addWidget(self.photo_preview)

        form.addRow(QLabel("姓名:"), self.name_input)
        form.addRow(QLabel("邮箱:"), self.email_input)
        form.addRow(QLabel("电话:"), self.phone_input)
        form.addRow(QLabel("照片:"), photo_layout)

        self.photo_button.clicked.connect(self.select_photo)

        group.setLayout(form)
        layout.addWidget(group)

    def create_academic_group(self, layout):
        group = QGroupBox("学术背景")
        form = QFormLayout()

        self.university_input = QLineEdit()
        self.major_input = QLineEdit()
        self.gpa_input = QLineEdit()
        self.awards_input = QTextEdit()
        self.research_input = QTextEdit()
        self.competitions_input = QTextEdit()

        # 设置文本编辑框高度和样式
        for text_edit in [self.awards_input, self.research_input, self.competitions_input]:
            text_edit.setFixedHeight(80)
            text_edit.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")

        form.addRow(QLabel("院校:"), self.university_input)
        form.addRow(QLabel("专业:"), self.major_input)
        form.addRow(QLabel("GPA:"), self.gpa_input)
        form.addRow(QLabel("获奖经历:"), self.awards_input)
        form.addRow(QLabel("科研经历:"), self.research_input)
        form.addRow(QLabel("竞赛经历:"), self.competitions_input)

        group.setLayout(form)
        layout.addWidget(group)

    def create_target_group(self, layout):
        group = QGroupBox("申请目标")
        form = QFormLayout()

        self.target_type = QComboBox()
        self.target_type.addItems(["留学申请文书", "求职简历"])

        self.target_input = QTextEdit()
        self.target_input.setPlaceholderText("输入目标院校/专业 或 公司/职位")
        self.target_input.setFixedHeight(80)
        self.target_input.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")

        form.addRow(QLabel("文书类型:"), self.target_type)
        form.addRow(QLabel("申请目标:"), self.target_input)

        group.setLayout(form)
        layout.addWidget(group)

    def create_progress_bar(self, layout):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3498db;
                border-radius: 5px;
                text-align: center;
                background: #f0f0f0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)

    def create_action_buttons(self, layout):
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("生成文书")
        self.preview_btn = QPushButton("预览PDF")
        self.export_btn = QPushButton("导出LaTeX")

        # 设置按钮样式
        btn_style = """
            QPushButton {
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """
        self.generate_btn.setStyleSheet(btn_style + "background-color: #3498db; color: white;")
        self.preview_btn.setStyleSheet(btn_style + "background-color: #2ecc71; color: white;")
        self.export_btn.setStyleSheet(btn_style + "background-color: #9b59b6; color: white;")

        self.generate_btn.clicked.connect(self.generate_document)
        self.preview_btn.clicked.connect(self.preview_pdf)
        self.export_btn.clicked.connect(self.export_latex)

        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

    def select_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择个人照片", "", "图片文件 (*.png *.jpg *.jpeg)"
        )
        if path:
            self.photo_path = path
            pixmap = QPixmap(path).scaled(
                100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.photo_preview.setPixmap(pixmap)

    def generate_document(self):
        # 验证API密钥
        api_key = self.api_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API密钥缺失", "请输入有效的DeepSeek API密钥")
            return

        # 收集用户数据
        user_data = self.collect_user_data()

        # 根据文书类型构建不同的提示词
        if "留学" in self.target_type.currentText():
            prompt = self.build_study_abroad_prompt(user_data)
        else:
            prompt = self.build_job_application_prompt(user_data)

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("正在生成文书内容...")

        # 确定模型
        model = "deepseek-chat"
        if "R1" in self.model_combo.currentText():
            model = "deepseek-reasoner"

        # 启动后台线程调用DeepSeek API
        self.worker = DeepSeekAPIWorker(api_key, prompt, model)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.handle_api_response)
        self.worker.start()

    def collect_user_data(self):
        """收集所有用户输入数据"""
        return {
            "name": self.name_input.text(),
            "email": self.email_input.text(),
            "phone": self.phone_input.text(),
            "university": self.university_input.text(),
            "major": self.major_input.text(),
            "gpa": self.gpa_input.text(),
            "awards": self.awards_input.toPlainText(),
            "research": self.research_input.toPlainText(),
            "competitions": self.competitions_input.toPlainText(),
            "target": self.target_input.toPlainText(),
            "doc_type": self.target_type.currentText(),
            "photo_path": self.photo_path
        }

    def build_study_abroad_prompt(self, data):
        """构建留学申请文书提示词"""
        return f"""
        你是一位专业的留学申请文书写作专家，请根据以下信息为申请人{data['name']}撰写一份留学申请文书：要求返回latex格式
        的代码，能够正常使用latex编译，注意，输出的文件内容应该符合留学申请文书个人陈述的要求，内容应该均为英文。

        ## 申请目标
        {data['target']}

        ## 个人信息
        - 姓名：{data['name']}
        - 邮箱：{data['email']}
        - 电话：{data['phone']}

        ## 教育背景
        - 院校：{data['university']}
        - 专业：{data['major']}
        - GPA：{data['gpa']}

        ## 经历与成就
        - 获奖经历：{data['awards']}
        - 科研经历：{data['research']}
        - 竞赛经历：{data['competitions']}

        ## 写作要求
        1. 文书应突出申请人的学术能力和研究潜力
        2. 结合申请目标说明申请动机
        3. 展现个人特质和独特优势
        4. 结构清晰，语言专业流畅
        5. 长度在800-1000字左右
        """

    def build_job_application_prompt(self, data):
        """构建求职简历提示词"""
        return f"""
        你是一位专业的求职简历写作专家，请根据以下信息为申请人{data['name']}撰写一份求职简历的自我评价部分，要求返回latex格式
        的代码，能够正常使用latex编译。简历应该美观，内容清晰。

        ## 申请目标
        {data['target']}

        ## 个人信息
        - 姓名：{data['name']}
        - 邮箱：{data['email']}
        - 电话：{data['phone']}

        ## 教育背景
        - 院校：{data['university']}
        - 专业：{data['major']}
        - GPA：{data['gpa']}

        ## 经历与成就
        - 获奖经历：{data['awards']}
        - 科研经历：{data['research']}
        - 竞赛经历：{data['competitions']}

        ## 写作要求
        1. 突出与目标职位相关的技能和经验
        2. 量化成就和贡献
        3. 展现职业素养和团队合作能力
        4. 语言精练专业，长度在300-500字
        5. 格式使用Markdown，包含标题和项目符号
        """

    def handle_api_response(self, content, success):
        """处理API返回结果"""
        self.progress_bar.setVisible(False)

        if success:
            self.generated_content = content
            self.statusBar().showMessage("文书内容生成成功!", 5000)

            # 生成LaTeX文档
            user_data = self.collect_user_data()
            doc = self.create_latex_document(user_data, content)

            # 生成唯一的文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_type = "study" if "留学" in user_data['doc_type'] else "job"
            filename = f"{doc_type}_application_{timestamp}.tex"
            tex_path = os.path.join(OUTPUT_DIR, filename)

            # 保存文件到output目录
            doc.generate_tex(tex_path)
            self.generated_tex_path = tex_path

            # 显示预览
            preview_dialog = QMessageBox(self)
            preview_dialog.setWindowTitle("生成预览")
            preview_dialog.setTextFormat(Qt.RichText)
            preview_dialog.setText(f"<h3>文书内容预览</h3><p>{content[:1000]}...</p>")
            preview_dialog.setDetailedText(f"文件已保存至: {tex_path}")
            preview_dialog.exec_()
        else:
            QMessageBox.critical(self, "生成失败", f"文书生成失败:\n{content}")

    def create_latex_document(self, data, generated_content):
        """创建包含生成内容的LaTeX文档"""
        doc = Document(documentclass="article")

        # 添加LaTeX包
        doc.preamble.append(Command("usepackage", "graphicx"))
        doc.preamble.append(Command("usepackage", "xcolor"))
        doc.preamble.append(Command("usepackage", "fontspec"))
        doc.preamble.append(Command("usepackage", ["geometry", "a4paper", "margin=1.5cm"]))
        doc.preamble.append(Command("usepackage", "parskip"))

        # 设置中文字体
        doc.preamble.append(NoEscape(r"\setmainfont{Noto Serif CJK SC}"))
        doc.preamble.append(NoEscape(r"\setsansfont{Noto Sans CJK SC}"))

        # 文档标题
        doc.preamble.append(Command("title", f"{data['doc_type']} - {data['name']}"))
        doc.preamble.append(Command("author", data['name']))
        doc.append(NoEscape(r"\maketitle"))

        # 添加照片部分
        if data["photo_path"]:
            # 复制照片到输出目录
            try:
                photo_filename = os.path.basename(data["photo_path"])
                output_photo_path = os.path.join(OUTPUT_DIR, photo_filename)

                # 如果照片不在输出目录，则复制过去
                if not os.path.exists(output_photo_path):
                    import shutil
                    shutil.copy(data["photo_path"], output_photo_path)

                with doc.create(Figure(position="h!")) as photo_fig:
                    photo_fig.add_image(photo_filename, width=NoEscape(r"0.2\textwidth"))
                    photo_fig.add_caption("个人照片")
            except Exception as e:
                print(f"照片处理错误: {str(e)}")

        # 联系信息部分
        with doc.create(Section("联系方式")):
            doc.append(f"姓名: {data['name']}\n\n")
            doc.append(f"邮箱: {data['email']}\n\n")
            doc.append(f"电话: {data['phone']}\n\n")

        # 教育背景部分
        with doc.create(Section("教育背景")):
            doc.append(f"{data['university']} | {data['major']}\n\n")
            doc.append(f"GPA: {data['gpa']}\n\n")

        # 添加AI生成的内容
        if "留学" in data['doc_type']:
            with doc.create(Section("申请陈述")):
                doc.append(NoEscape(generated_content.replace("\n\n", "\n\n")))
        else:
            with doc.create(Section("求职意向")):
                doc.append(f"目标职位: {data['target']}\n\n")
            with doc.create(Section("个人陈述")):
                doc.append(NoEscape(generated_content.replace("\n\n", "\n\n")))

        # 添加成就部分
        if data['awards']:
            with doc.create(Section("获奖经历")):
                doc.append(NoEscape(data['awards'].replace("\n", "\n\n")))

        if data['research']:
            with doc.create(Section("科研经历")):
                doc.append(NoEscape(data['research'].replace("\n", "\n\n")))

        if data['competitions']:
            with doc.create(Section("竞赛经历")):
                doc.append(NoEscape(data['competitions'].replace("\n", "\n\n")))

        return doc

    def preview_pdf(self):
        if not hasattr(self, "generated_tex_path") or not self.generated_tex_path:
            self.statusBar().showMessage("请先生成文书", 3000)
            return

        # 在实际应用中应调用pdflatex编译
        tex_file = self.generated_tex_path
        pdf_path = tex_file.replace(".tex", ".pdf")

        # 检查系统是否安装了pdflatex
        if os.system("pdflatex --version") == 0:
            # 在output目录中编译
            os.chdir(OUTPUT_DIR)
            os.system(f"pdflatex {os.path.basename(tex_file)}")

            if os.path.exists(pdf_path):
                # 跨平台打开PDF文件
                if sys.platform == "win32":
                    os.startfile(pdf_path)
                elif sys.platform == "darwin":  # macOS
                    os.system(f"open '{pdf_path}'")
                else:  # Linux
                    os.system(f"xdg-open '{pdf_path}'")
            else:
                QMessageBox.warning(self, "PDF生成失败", "无法生成PDF文件，请检查LaTeX安装")
        else:
            QMessageBox.information(
                self,
                "PDF预览",
                "PDF预览需要安装LaTeX环境(如MiKTeX或TeX Live)\n"
                f"生成的LaTeX文件已保存至: {self.generated_tex_path}"
            )

    def export_latex(self):
        if not hasattr(self, "generated_tex_path") or not self.generated_tex_path:
            self.statusBar().showMessage("请先生成文书", 3000)
            return

        # 保存LaTeX文件
        default_filename = os.path.basename(self.generated_tex_path)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存LaTeX文件", os.path.join(OUTPUT_DIR, default_filename), "LaTeX文件 (*.tex)"
        )

        if file_path:
            if not file_path.endswith(".tex"):
                file_path += ".tex"

            try:
                with open(self.generated_tex_path, "r", encoding="utf-8") as src:
                    with open(file_path, "w", encoding="utf-8") as dest:
                        dest.write(src.read())
                self.statusBar().showMessage(f"LaTeX文件已保存: {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"文件保存失败:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 1px solid #3498db;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            background-color: #3498db;
            color: white;
            border-radius: 3px;
        }
        QLabel {
            font-size: 12px;
        }
        QLineEdit, QTextEdit {
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 5px;
        }
    """)

    window = ResumeGeneratorApp()
    window.show()
    sys.exit(app.exec_())