from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('SELECT visibility, COUNT(*) FROM community_posts GROUP BY visibility'))
print("Visibility values in database:")
for row in result:
    print(f'  {row[0]}: {row[1]}')

result2 = db.execute(text('SELECT id, title, visibility FROM community_posts LIMIT 3'))
print("\nSample posts:")
for row in result2:
    print(f'  {row[1]}: visibility={row[2]}')

db.close()
