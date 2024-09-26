import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Lista para armazenar os cartões
cartoes = []
# Variável global para armazenar os cartões selecionados
selecionados = []
# Dicionário para rastrear os usuários e seus tempos de início
user_start_times = {}

# Função que responde ao comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    current_time = time.time()

    # Verifica se o usuário já iniciou o bot recentemente
    if user_id in user_start_times:
        last_start_time = user_start_times[user_id]
        if current_time - last_start_time < 30:  # 30 segundos = 30 segundos
            remaining_time = 30 - (current_time - last_start_time)
            await update.message.reply_text(f"Você deve esperar {int(remaining_time)} segundos antes de iniciar o Bot novamente.")
            return

    # Atualiza o tempo do último início
    user_start_times[user_id] = current_time

    keyboard = [
        [InlineKeyboardButton("💳 | Gerar meus Cartões", callback_data='generate_cards'),
         InlineKeyboardButton("📚 | Tutorial", callback_data='tutorial')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        """
Seja bem-vindo ao <b>ND Gerador</b>!
Clique no botão abaixo para gerar um total de <b>10</b> cartões validados.""",
        reply_markup=reply_markup,
        parse_mode='HTML'  # Usando HTML para permitir a formatação
    )

# Função para adicionar cartões à lista
async def add_cartoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global cartoes
    novos_cartoes = context.args
    cartoes.extend(novos_cartoes)
    await update.message.reply_text(f"{len(novos_cartoes)} cartões adicionados!")

# Função que trata o callback do botão
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global selecionados  # Declarar a variável como global
    query = update.callback_query
    await query.answer()  # Para remover o indicador de carregamento

    if query.data == 'generate_cards':
        if len(cartoes) < 10:
            await query.edit_message_text(text="Estamos em manutenção, aguarde...")
            return
        
        # Seleciona 10 cartões aleatórios
        selecionados = random.sample(cartoes, 10)
        # Formata os cartões em monoespaçado
        formatted_cartoes = "```\n" + "\n".join(selecionados) + "\n```"
        
        # Adiciona um botão para copiar
        copiar_keyboard = [
            [InlineKeyboardButton("⚙️ | Copiar Cartões manualmente", callback_data='copy_cards')]
        ]
        copiar_markup = InlineKeyboardMarkup(copiar_keyboard)

        await query.edit_message_text(
            text=formatted_cartoes,  # Apenas os cartões
            reply_markup=copiar_markup,
            parse_mode='MarkdownV2'  # Usando MarkdownV2 para monoespaçado
        )

    elif query.data == 'copy_cards':
        await query.edit_message_text(text="\n" + "\n".join(selecionados), parse_mode='HTML')  # Sem formatação

    elif query.data == 'tutorial':
        await enviar_tutorial(query)

# Função para enviar o tutorial
async def enviar_tutorial(query):
    tutorial_message = ("""
📚 | Tutorial de como usar o Bot:

1. <b>Gerar Cartões</b>: Clique no botão '<b>Gerar meus Cartões</b>' para obter <b>10</b> Cartões validados e aleatórios.
2. <b>Copiar Cartões</b>: Os Cartões serão enviados em Monoespaçado, basta clicar nos Cartões que todos serão copiados automaticamente.
3. <b>Copiar Cartões manualmente</b>: Caso você queira copiar seus Cartões manualmente, basta clicar no botão '<b>Copiar Cartões manualmente</b>' que eles serão enviados em texto normal.
4. <b>Voltar ao menu</b>: Para voltar ao menu, ou iniciar o Bot novamente, basta clicar na opção '<b>Menu</b>' ou escrever o comando '/start' e enviar."""
    )
    
    await query.edit_message_text(text=tutorial_message, parse_mode='HTML')

# Função para o comando /tutorial
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await enviar_tutorial(update)

def main() -> None:
    app = ApplicationBuilder().token("YOUR_TOKEN").build()  # Substitua YOUR_TOKEN pelo seu token real

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_cartoes", add_cartoes))
    app.add_handler(CommandHandler("tutorial", tutorial))  # Adicionando o comando /tutorial
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == '__main__':
    main()
