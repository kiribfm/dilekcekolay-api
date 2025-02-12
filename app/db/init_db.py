from app.db.database import create_tables

def init_db():
    create_tables()
    print("Veritabanı tabloları başarıyla oluşturuldu!")

if __name__ == "__main__":
    init_db() 