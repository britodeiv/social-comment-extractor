# Social Comment Extractor v3.0

Automação desktop desenvolvida em Python para extração de comentários de redes sociais utilizando Selenium + CustomTkinter.

---

## Preview
<img width="1376" height="881" alt="print" src="https://github.com/user-attachments/assets/7fbf76d5-afa8-4425-83a9-a4060d0f5167" />
<img width="1376" height="854" alt="print 2" src="https://github.com/user-attachments/assets/c63acb74-0e88-48c5-ba89-c850c5f75f6d" />
<img width="1339" height="814" alt="print 3" src="https://github.com/user-attachments/assets/29e63d30-be6a-40b3-b176-1105cd4672ec" />
<img width="1356" height="883" alt="print 4" src="https://github.com/user-attachments/assets/3ad80837-d205-48bf-911d-6137bbf68ba0" />





---

# Funcionalidades

* Extração automática de comentários
* Suporte para:

  * Facebook
  * YouTube
  * X / Twitter
* Exportação para Excel (.xlsx)
* Interface gráfica moderna com CustomTkinter
* Contador em tempo real
* Barra de progresso
* Sistema de logs
* Abertura automática de respostas/comentários ocultos
* Scroll automático inteligente

---

# Tecnologias Utilizadas

* Python
* Selenium
* CustomTkinter
* Pandas
* WebDriver Manager

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/britodeiv/social-comment-extractor.git
```

Entre na pasta:

```bash
cd social-comment-extractor
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python app.py
```

---

# Gerar Executável (.EXE)

```bash
pyinstaller --onefile --windowed --collect-all selenium app.py
```

O executável será criado em:

```text
/dist
```

---

# Estrutura do Projeto

```text
social-comment-extractor/
│
├── extrator.py
├── README.md
├── /dist
├── /build
└── /images
```

---

# Screenshots

## Interface

Adicione imagens aqui.

---

# Melhorias Futuras

* Login automático
* Exportação CSV
* Suporte Instagram
* Suporte TikTok
* Sistema anti-bloqueio
* Modo headless
* Dashboard de métricas

---

# Aviso

Este projeto foi desenvolvido apenas para fins educacionais e automação pessoal.

O uso deve respeitar os termos de uso de cada plataforma.

---

# Autor

Desenvolvido por britodeiv.

GitHub:

```text
https://github.com/britodeiv
```

---

# Licença

MIT License
