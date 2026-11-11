from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QTextBrowser)


from searching_engine import search_and_rank_parallel
from loader import combined_data


class SearchEngineWindow(QMainWindow):
    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset
        self.setWindowTitle("Suchmaschine - KIT Mathematik")
        self.resize(750, 550)
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Text eingeben...")
        self.query_input.returnPressed.connect(self.on_search) 

        self.search_btn = QPushButton("Suchen")
        self.search_btn.clicked.connect(self.on_search)

        search_layout.addWidget(self.query_input)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        self.results_display = QTextBrowser()
        self.results_display.setOpenExternalLinks(True) 
        main_layout.addWidget(self.results_display)

    def on_search(self):
        query = self.query_input.text().strip()
        if not query:
            return

    
        results = search_and_rank_parallel(query, self.dataset)

        if not results:
            self.results_display.setHtml("<p style='color: red;'>Keine Ergebnisse gefunden.</p>")
            return
          
        html = f"<h4>Ergebnisse gefunden: {len(results)}</h4><hr>"
        for item in results:
            html += f"""
            <div style="margin-bottom: 15px;">
                <a href="{item['url']}" style="font-size: 15px; font-weight: bold; text-decoration: none;">
                    {item['title']}
                </a> 
                <span style="color: #666; font-size: 11px;">(PR: {item['weight']:.4f})</span><br>
                <span style="color: #006621; font-size: 12px;">{item['url']}</span>
                <p style="margin-top: 4px; color: #333;">{item['snippet']}</p>
            </div>
            """
        self.results_display.setHtml(html)


if __name__ == "__main__":
    app = QApplication([])
    
    data = combined_data
    
    window = SearchEngineWindow(data)
    window.show()
    
    app.exec()
