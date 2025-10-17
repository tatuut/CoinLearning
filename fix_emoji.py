"""絵文字を置換するスクリプト"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 絵文字を置換
content = content.replace('❌', '[NG]')
content = content.replace('✅✅', '[STRONG]')
content = content.replace('✅', '[OK]')
content = content.replace('🔍', '[*]')
content = content.replace('📊', '[CHART]')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('絵文字を置換しました')
