from app import app, db, Produto
import os

with app.app_context():
    count = Produto.query.count()
    if count < 6:
        print(f"Current product count: {count}. Adding more...")
        
        produtos_demo = [
            {"nome": "Abacaxi Pérola", "descricao": "Abacaxi doce e suculento, perfeito para sobremesas e sucos.", "preco": 8.50, "imagem": "abacaxi.jpg"},
            {"nome": "Banana Nanica", "descricao": "Bananas maduras e ricas em potássio. Ótimas para o café da manhã.", "preco": 4.90, "imagem": "banana.jpg"},
            {"nome": "Maçã Gala", "descricao": "Maçãs crocantes e fresquinhas da estação.", "preco": 6.20, "imagem": "maca.jpg"},
            {"nome": "Uva sem Semente", "descricao": "Uvas doces e práticas para o lanche das crianças.", "preco": 12.00, "imagem": "uva.jpg"},
            {"nome": "Morango Selecionado", "descricao": "Morangos vermelhos e selecionados manualmente.", "preco": 9.50, "imagem": "morango.jpg"},
            {"nome": "Manga Palmer", "descricao": "Manga sem fiapo, extremamente doce e carnuda.", "preco": 7.80, "imagem": "manga.jpg"}
        ]
        
        for p_data in produtos_demo[count:]:
            p = Produto(
                nome=p_data["nome"],
                descricao=p_data["descricao"],
                preco=p_data["preco"],
                imagem=p_data["imagem"]
            )
            db.session.add(p)
        
        db.session.commit()
        print("Database seeded with 6 products.")
    else:
        print(f"Database already has {count} products.")
