import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkComboBox, CTkProgressBar, CTkTextbox
from tkinter import filedialog, messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import threading
import time
import os
import tempfile
from datetime import datetime


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Social Comment Extractor v3.0")
        self.geometry("1400x900")
        self.resizable(True, True)

        self.driver = None
        self.rodando = False
        self.total = 0
        self.dados = []

        self._build_ui()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):

        main = CTkFrame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        CTkLabel(
            main,
            text="Social Comment Extractor v3.0",
            font=("Arial", 24, "bold")
        ).pack(pady=10)

        # URL + Rede
        input_frame = CTkFrame(main)
        input_frame.pack(fill="x", padx=10, pady=10)

        CTkLabel(input_frame, text="URL:").pack(side="left", padx=5)

        self.url_entry = CTkEntry(
            input_frame,
            placeholder_text="Cole a URL do post (Facebook, YouTube ou X)..."
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)

        CTkLabel(input_frame, text="Rede:").pack(side="left", padx=5)

        self.network_combo = CTkComboBox(
            input_frame,
            values=["Facebook", "YouTube test", "X"],
            state="readonly",
            width=130
        )
        self.network_combo.set("Facebook")
        self.network_combo.pack(side="left", padx=5)

        # Botões
        btn_frame = CTkFrame(main)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.start_btn = CTkButton(
            btn_frame,
            text="START",
            fg_color="#00AA00",
            hover_color="#008800",
            command=self.start
        )
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = CTkButton(
            btn_frame,
            text="STOP",
            fg_color="#DD0000",
            hover_color="#BB0000",
            state="disabled",
            command=self.stop
        )
        self.stop_btn.pack(side="left", padx=5)

        self.export_btn = CTkButton(
            btn_frame,
            text="EXPORTAR",
            state="disabled",
            command=self.exportar
        )
        self.export_btn.pack(side="left", padx=5)

        # Barra de progresso
        prog_frame = CTkFrame(main)
        prog_frame.pack(fill="x", padx=10, pady=10)

        CTkLabel(prog_frame, text="Progresso:").pack(side="left", padx=5)

        self.progress_bar = CTkProgressBar(prog_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.progress_bar.set(0)

        # Status + contador
        status_frame = CTkFrame(main)
        status_frame.pack(fill="x", padx=10, pady=10)

        CTkLabel(status_frame, text="Status:").pack(side="left", padx=5)

        self.status_label = CTkLabel(
            status_frame,
            text="IDLE",
            font=("Arial", 14, "bold"),
            text_color="#FFAA00"
        )
        self.status_label.pack(side="left", padx=5)

        CTkLabel(status_frame, text="Comentarios:").pack(side="left", padx=20)

        self.count_label = CTkLabel(
            status_frame,
            text="0",
            font=("Arial", 14, "bold"),
            text_color="#00AAFF"
        )
        self.count_label.pack(side="left", padx=5)

        # Log
        log_frame = CTkFrame(main)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        CTkLabel(
            log_frame,
            text="Log:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.log_box = CTkTextbox(log_frame, state="normal")
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Rodapé
        CTkLabel(
            main,
            text="v3.0 | Social Comment Extractor |  Desenvolvido por britodeiv",
            text_color="gray",
            font=("Arial", 10)
        ).pack(pady=5)

    # =========================================================
    # HELPERS UI
    # =========================================================

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        linha = f"[{ts}] {msg}\n"
        self.log_box.insert("end", linha)
        self.log_box.see("end")
        self.update_idletasks()

    def set_status(self, texto: str, cor: str = "#FFAA00"):
        self.status_label.configure(text=texto, text_color=cor)

    def set_count(self, n: int):
        self.count_label.configure(text=str(n))
        self.progress_bar.set(min(n / 500, 1.0))

    # =========================================================
    # DRIVER
    # =========================================================

    def iniciar_driver(self):

        options = Options()

        profile_dir = os.path.join(
            tempfile.gettempdir(),
            "chrome_profile_extrator"
        )

        options.add_argument("--user-data-dir=" + profile_dir)
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.execute_script("""
            Object.defineProperty(navigator,'webdriver',{get:()=>undefined})
        """)

        return driver

    # =========================================================
    # START / STOP / EXPORTAR
    # =========================================================

    def start(self):

        if self.rodando:
            return

        self.rodando = True
        self.total = 0
        self.dados = []

        self.set_count(0)
        self.progress_bar.set(0)
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        self.set_status("INICIANDO", "#FFAA00")

        threading.Thread(target=self.extrair, daemon=True).start()

    def stop(self):

        self.rodando = False

        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

        self.driver = None

        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.set_status("PARADO", "#FF5500")
        self.log("Extração parada pelo usuário.")

    def exportar(self):

        if not self.dados:
            messagebox.showwarning("Aviso", "Nenhum dado para exportar.")
            return

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="comentarios_{}.xlsx".format(int(time.time()))
        )

        if arquivo:
            df = pd.DataFrame(self.dados)
            df.to_excel(arquivo, index=False)
            messagebox.showinfo("Exportado", f"{len(self.dados)} comentários salvos.")
            self.log(f"Arquivo salvo: {arquivo}")

    # =========================================================
    # EXTRAÇÃO PRINCIPAL
    # =========================================================

    def extrair(self):

        url = self.url_entry.get().strip()

        try:

            self.log("Inicializando Selenium...")
            self.set_status("INICIALIZANDO", "#FFAA00")

            self.driver = self.iniciar_driver()
            driver = self.driver

            self.log(f"Navegando para: {url}")
            self.set_status("NAVEGANDO", "#00AAFF")

            driver.get(url)
            time.sleep(8)

            # ===================================================
            # FACEBOOK
            # ===================================================

            if "facebook.com" in url:

                self.set_status("EXTRAINDO", "#AA00AA")
                self.log("Plataforma: Facebook")

                try:
                    menu = driver.find_element(
                        By.XPATH,
                        "//span[contains(text(),'Mais relevantes') "
                        "or contains(text(),'Todos os comentários') "
                        "or contains(text(),'Mais recentes')]"
                    )
                    driver.execute_script("arguments[0].click();", menu)
                    time.sleep(1)

                    opcao = driver.find_element(
                        By.XPATH,
                        "//*[contains(text(),'Todos os comentários')]"
                    )
                    driver.execute_script("arguments[0].click();", opcao)
                    time.sleep(2)
                    self.log("Ordenação: Todos os comentários")
                except:
                    pass

                comentarios_unicos = set()
                respostas_abertas = set()
                contador_sem_novos = 0
                ultimo_altura = 0

                for ciclo in range(500):

                    if not self.rodando:
                        break

                    # Scroll em containers internos
                    try:
                        containers = driver.find_elements(
                            By.XPATH, "//div[contains(@style,'overflow')]"
                        )
                        for c in containers:
                            try:
                                driver.execute_script(
                                    "arguments[0].scrollTop=arguments[0].scrollHeight;", c
                                )
                            except:
                                pass
                    except:
                        pass

                    # Abrir respostas
                    try:
                        botoes_resposta = driver.find_elements(
                            By.XPATH, "//div[@role='button']//span"
                        )
                        for botao in botoes_resposta:
                            try:
                                texto = botao.text.strip().lower()
                                if not texto:
                                    continue
                                termos = [
                                    "ver 1 resposta", "ver mais respostas",
                                    "ver todas as respostas", "ver todas as",
                                    "1 resposta", "2 respostas", "3 respostas",
                                    "4 respostas", "5 respostas", "resposta"
                                ]
                                if not any(t in texto for t in termos):
                                    continue
                                elemento = botao.find_element(
                                    By.XPATH, "./ancestor::div[@role='button'][1]"
                                )
                                chave = elemento.id
                                if chave in respostas_abertas:
                                    continue
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block:'center'});", elemento
                                )
                                time.sleep(0.2)
                                driver.execute_script("arguments[0].click();", elemento)
                                respostas_abertas.add(chave)
                                time.sleep(1)
                            except:
                                pass

                        driver.execute_script("window.scrollBy(0,3500);")
                    except:
                        pass

                    time.sleep(1)

                    novo_total = len(driver.find_elements(By.XPATH, "//div[@role='article']"))
                    altura_atual = driver.execute_script("return document.body.scrollHeight")

                    self.set_status(f"SCROLLING FB ({ciclo})", "#FFAA00")
                    self.log(f"Ciclo {ciclo} | artigos: {novo_total} | altura: {altura_atual}")

                    if altura_atual == ultimo_altura:
                        contador_sem_novos += 1
                    else:
                        contador_sem_novos = 0

                    ultimo_altura = altura_atual

                    if contador_sem_novos >= 80:
                        self.log("Página estabilizada. Coletando...")
                        break

                # Coleta final
                self.set_status("COLETANDO", "#00AAFF")
                comentarios = driver.find_elements(By.XPATH, "//div[@role='article']")

                for c in comentarios:
                    try:
                        texto = c.text.strip()
                        linhas = texto.split("\n")
                        if len(linhas) < 2:
                            continue
                        usuario = linhas[0].strip()
                        comentario = " ".join(linhas[1:]).strip().replace("\n", " ")[:2000]
                        chave = usuario + "::" + comentario
                        if chave in comentarios_unicos:
                            continue
                        comentarios_unicos.add(chave)
                        self.dados.append({
                            "Usuario": usuario,
                            "Comentario": comentario,
                            "Rede": "Facebook"
                        })
                        self.total += 1
                        self.set_count(self.total)
                    except:
                        pass

            # ===================================================
            # YOUTUBE
            # ===================================================

            elif "youtube.com" in url:

                self.set_status("EXTRAINDO", "#AA00AA")
                self.log("Plataforma: YouTube")

                contador_sem_novos = 0
                ultimo = 0

                for ciclo in range(300):

                    if not self.rodando:
                        break

                    driver.execute_script("window.scrollBy(0,3000);")
                    time.sleep(1)

                    # Abrir respostas
                    try:
                        botoes = driver.find_elements(
                            By.XPATH,
                            "//*[contains(text(),'resposta') or contains(text(),'reply')]"
                        )
                        for b in botoes:
                            try:
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block:'center'});", b
                                )
                                time.sleep(0.2)
                                driver.execute_script("arguments[0].click();", b)
                                time.sleep(0.5)
                            except:
                                pass
                    except:
                        pass

                    comentarios = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
                    novo_total = len(comentarios)

                    self.set_status(f"SCROLLING YT ({ciclo})", "#FFAA00")

                    if ciclo % 10 == 0:
                        self.log(f"Ciclo {ciclo} | comentários visíveis: {novo_total}")

                    if novo_total == ultimo:
                        contador_sem_novos += 1
                    else:
                        contador_sem_novos = 0

                    ultimo = novo_total

                    if contador_sem_novos >= 30:
                        self.log("Página estabilizada. Coletando...")
                        break

                # Coleta final
                self.set_status("COLETANDO", "#00AAFF")
                comentarios_unicos = set()
                comentarios = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

                for c in comentarios:
                    try:
                        texto = c.text.strip().replace("\n", " ")
                        if len(texto) < 2:
                            continue
                        try:
                            container = c.find_element(
                                By.XPATH, "./ancestor::ytd-comment-renderer[1]"
                            )
                        except:
                            container = c.find_element(
                                By.XPATH, "./ancestor::*[@id='comment'][1]"
                            )
                        try:
                            autor = container.find_element(
                                By.XPATH, './/*[@id="author-text"]'
                            ).text.strip()
                        except:
                            autor = "Sem nome"
                        chave = autor + "::" + texto
                        if chave in comentarios_unicos:
                            continue
                        comentarios_unicos.add(chave)
                        self.dados.append({
                            "Usuario": autor,
                            "Comentario": texto,
                            "Rede": "YouTube"
                        })
                        self.total += 1
                        self.set_count(self.total)
                    except:
                        pass

            # ===================================================
            # X / TWITTER
            # ===================================================

            elif "x.com" in url or "twitter.com" in url:

                self.set_status("EXTRAINDO", "#AA00AA")
                self.log("Plataforma: X/Twitter")

                comentarios_unicos = set()
                contador_sem_novos = 0
                ultimo = 0

                for ciclo in range(450):

                    if not self.rodando:
                        break

                    driver.execute_script("window.scrollBy(0,3500);")
                    time.sleep(1)

                    tweets = driver.find_elements(By.XPATH, "//article")

                    for t in tweets:
                        try:
                            textos = t.find_elements(By.XPATH, ".//div[@lang]")

                            partes_validas = []
                            lixo = ["visualizações", "views", "curtidas", "likes", "retweets", "reposts"]

                            for x in textos:
                                txt = x.text.strip()
                                if not txt:
                                    continue
                                if any(l in txt.lower() for l in lixo):
                                    continue
                                if txt.lower().startswith("@"):
                                    continue
                                partes_validas.append(txt)

                            comentario = " ".join(partes_validas).replace("\n", " ")
                            if len(comentario) < 3:
                                continue
                            try:
                                usuario = t.find_element(
                                    By.XPATH, ".//span[contains(text(),'@')]"
                                ).text.strip()
                            except:
                                usuario = "Sem nome"
                            chave = usuario + "::" + comentario
                            if chave in comentarios_unicos:
                                continue
                            comentarios_unicos.add(chave)
                            self.dados.append({
                                "Usuario": usuario,
                                "Comentario": comentario,
                                "Rede": "X"
                            })
                            self.total += 1
                            self.set_count(self.total)
                        except:
                            pass

                    novo_total = len(tweets)
                    self.set_status(f"SCROLLING X ({ciclo})", "#FFAA00")

                    if novo_total == ultimo:
                        contador_sem_novos += 1
                    else:
                        contador_sem_novos = 0

                    ultimo = novo_total

                    if contador_sem_novos >= 25:
                        self.log("Feed estabilizado. Finalizando...")
                        break

            # ===================================================
            # FIM
            # ===================================================

            try:
                driver.quit()
            except:
                pass

            self.driver = None
            self.rodando = False

            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

            if self.dados:
                self.export_btn.configure(state="normal")
                self.set_status("PRONTO", "#00FF00")
                self.log(f"Extração concluída! {len(self.dados)} comentários. Clique EXPORTAR.")
            else:
                self.set_status("SEM DADOS", "#FF5500")
                self.log("Nenhum comentário encontrado.")
                messagebox.showwarning("Aviso", "Nenhum comentário encontrado.")

        except Exception as e:

            self.log(f"ERRO: {str(e)}")
            self.set_status("ERRO", "#FF0000")
            self.rodando = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass

            self.driver = None
            messagebox.showerror("Erro", str(e))


# =========================================================
# EXECUTAR
# =========================================================

app = App()
app.mainloop()
