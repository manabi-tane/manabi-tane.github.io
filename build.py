#!/usr/bin/env python3
"""texts/*.js から各章段のページ・練習ページ・作品一覧を生成する。

新しい章段を足すときは texts/ に .js を 1 つ置いて、このスクリプトを実行するだけ。
    python3 build.py
"""
import os, re, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent

SITE = '学びのたね'
SITE_DESC = '高校の教科を、原典にあたりながら自分の手で確かめる学習サイト。'

# 教科。フォルダ名＝id。status が 'open' のものだけ中身がある。
SUBJECTS = [
    {'id':'kobun', 'name':'古典', 'sub':'古文・漢文', 'icon':'📜', 'status':'open',
     'desc':'教科書の名文を縦書きで読み、語をひらくと品詞・活用・意味・語法が出ます。'
            '頻出ポイントの一問一答と、単語・文法の練習つき。'},
    {'id':'eigo', 'name':'英語', 'sub':'構文・語法', 'icon':'📘', 'status':'soon',
     'desc':'英文を意味のまとまりごとに区切って読み、区切りごとの訳・全文訳・構文メモ・'
            '新出語を切り替えながら確かめられます。'},
    {'id':'sekaishi', 'name':'世界史', 'sub':'通史・史料', 'icon':'🌍', 'status':'soon',
     'desc':'できごとの前後関係と史料を結びつけて確かめられるようにする予定です。'},
]
PAGE_DIR = ''          # そのページがどのフォルダにあるか（'' は最上位）
# ふだんは手元のファイル（file://）で開くので ?v=ハッシュ は付けない。
# 公開用にビルドするときだけ CACHE_BUST=1 python3 build.py とする。
CACHE_BUST = os.environ.get('CACHE_BUST') == '1'
# 問い合わせ先。本名の入らない、このサイト専用のアドレスに差し替えてください。
CONTACT = 'manabi.tane.study@gmail.com'

# 収録順（時代順）。ここに無い id は末尾に並ぶ。
ORDER = [
    'taketori-oitachi', 'ise-azumakudari', 'ise-tsutsuizutsu',
    'ochikubo-tegami', 'makura-haruwa', 'makura-warewoba', 'genji-kiritsubo',
    'hojoki-yukukawa', 'heike-gion', 'heike-ougi',
    'tsurezure-joudan', 'tsurezure-ninnaji', 'tamakatsuma-inaka',
    'shiki-koumon',
]
# 一覧ページでのまとまり
GROUPS = [('物語・歌物語', {'物語', '歌物語'}),
          ('随筆',        {'随筆'}),
          ('軍記物語',    {'軍記物語'}),
          ('漢文',        {'漢文'})]
# 初回訪問時にお気に入りに入っている作品
DEFAULT_FAV_WORKS = ['玉勝間', '落窪物語', '枕草子', '源氏物語']

FIELDS = ('id', 'work', 'title', 'chapter', 'author', 'era', 'genre', 'range', 'lede')
FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
           "<text y='26' x='4' font-size='26'>%F0%9F%93%9C</text></svg>")
e = html.escape


def fonts():
    """書体は自前で配る。外部への接続をゼロにするため。"""
    return '<link rel="stylesheet" href="%s">' % ver('assets/fonts.css')


def ver(rel):
    """ROOT からの相対パスを、いま作っているページから見た相対パスに直し、
    内容ハッシュを付ける（ブラウザの古いキャッシュ対策）。"""
    f = ROOT / rel
    if PAGE_DIR and rel.startswith(PAGE_DIR + '/'):
        out = rel[len(PAGE_DIR) + 1:]
    elif PAGE_DIR:
        out = '../' + rel
    else:
        out = rel
    if not f.exists() or not CACHE_BUST:
        return out
    import hashlib
    return out + '?v=' + hashlib.sha1(f.read_bytes()).hexdigest()[:8]


def up(path=''):
    """最上位から見たパスを、いまのページからのリンクに直す。"""
    return ('../' if PAGE_DIR else '') + path


def load():
    works = []
    for path in sorted((ROOT / 'kobun' / 'texts').glob('*.js')):
        src = path.read_text(encoding='utf-8')
        w = {}
        for key in FIELDS:
            m = re.search(r"\n\s*%s\s*:\s*'((?:[^'\\]|\\.)*)'" % key, src)
            w[key] = m.group(1) if m else ''
        if not w['id']:
            raise SystemExit('id が見つかりません: %s' % path.name)
        w['file'] = path.name
        w['words'] = len(re.findall(r"W\('", src))
        w['aux'] = len(re.findall(r",\s*'aux'\s*,", src))
        works.append(w)
    works.sort(key=lambda w: (ORDER.index(w['id']) if w['id'] in ORDER else 99, w['id']))
    return works


def head(title, desc, body_class=''):
    return ('<!doctype html>\n<html lang="ja">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="color-scheme" content="light dark">\n'
            '<meta name="description" content="%s">\n<title>%s</title>\n'
            '<link rel="icon" href="%s">\n%s\n'
            '<link rel="stylesheet" href="%s">\n</head>\n<body%s>\n'
            % (e(desc, quote=True), e(title), FAVICON, fonts(), ver('assets/style.css'),
               ' class="%s"' % body_class if body_class else ''))


def foot():
    return ('<footer class="sitefoot">\n'
            '  <nav aria-label="サイトの案内">\n'
            '    <a href="%s">ホーム</a><a href="%s">プライバシーポリシー</a>'
            '<a href="%s">利用規約</a><a href="%s">Cookie とデータの扱い</a>\n'
            '  </nav>\n'
            '  <p>本文は著作権の切れた古典。解説・現代語訳・設問はこのサイトで書き起こしたものです。<br>'
            '個人が趣味で運営している無料の学習サイトで、広告・課金・アクセス解析はありません。</p>\n'
            '</footer>\n' % (up('index.html'), up('privacy.html'), up('terms.html'), up('cookies.html')))


def star(work_id):
    return ('<button class="star" data-fav-id="%s" aria-pressed="false" '
            'aria-label="お気に入りに入れる">★</button>' % e(work_id))


CONTROLS = '''  <div class="tools">
    <div class="grp" id="hlchips">
      <span class="lab">品詞を強調</span>
      <button class="chip aux" data-hl="aux" aria-pressed="false"><span class="dot"></span>助動詞</button>
      <button class="chip v" data-hl="v" aria-pressed="false"><span class="dot"></span>動詞</button>
      <button class="chip adj" data-hl="adj" aria-pressed="false"><span class="dot"></span>形容</button>
      <button class="chip pt" data-hl="pt" aria-pressed="false"><span class="dot"></span>助詞</button>
      <button class="chip n" data-hl="n" aria-pressed="false"><span class="dot"></span>名詞</button>
      <button class="chip o" data-hl="o" aria-pressed="false"><span class="dot"></span>その他</button>
      <button class="chip imp" data-hl="imp" aria-pressed="false"><span class="dot"></span>要チェック</button>
      <button class="chip spot" data-hl="spot" aria-pressed="false"><span class="dot"></span>頻出</button>
    </div>
    <div class="grp">
      <button class="chip kei" id="keiBtn" aria-pressed="true"><span class="dot"></span>敬語に圏点</button>
      <button class="chip plain" id="colorBtn" aria-pressed="true">品詞で色分け</button>
      <button class="chip plain" id="rubyBtn" aria-pressed="false">読み仮名</button>
      <button class="chip plain" id="hakuBtn" aria-pressed="false">白文</button>
      <button class="chip plain" id="yakuBtn" aria-pressed="false">現代語訳</button>
      <button class="chip plain" id="pdfBtn">PDF</button>
    </div>
    <div class="grp">
      <span class="lab">字</span>
      <div class="step">
        <button id="fsDown" title="小さく">小</button>
        <button id="fsUp" title="大きく">大</button>
      </div>
    </div>
  </div>
'''

PANEL = '''<main>
  <aside>
    <div class="tabs" role="tablist">
      <button role="tab" id="tab-w" aria-selected="true" aria-controls="pane-w">語　釈</button>
      <button role="tab" id="tab-a" aria-selected="false" aria-controls="pane-a">助動詞</button>
      <button role="tab" id="tab-k" aria-selected="false" aria-controls="pane-k">句法</button>
      <button role="tab" id="tab-s" aria-selected="false" aria-controls="pane-s">頻出</button>
    </div>
    <div class="pane" id="pane-w" role="tabpanel" aria-labelledby="tab-w"></div>
    <div class="pane" id="pane-a" role="tabpanel" aria-labelledby="tab-a" hidden></div>
    <div class="pane" id="pane-k" role="tabpanel" aria-labelledby="tab-k" hidden></div>
    <div class="pane" id="pane-s" role="tabpanel" aria-labelledby="tab-s" hidden></div>
    <div class="legend">
      本文の語をクリック／タップすると品詞・活用・意味が出ます。<br>
      <span class="sesame">圏点</span>は敬語、<span class="kuline">下線</span>は句法。矢印キーで前後の語へ移動。
    </div>
  </aside>
  <div id="scroll"><div id="text"></div></div>
</main>
'''


def work_page(w):
    return (head('%s｜%s — 古文リーダー' % (w['title'], w['work']), w['lede'])
            + '<a class="skip" href="#scroll">本文へスキップ</a>\n'
              '<header>\n'
              '  <a class="back" href="index.html">← 作品一覧</a>\n'
              '  %s\n'
              '  <div class="brand">\n    <h1>%s</h1>\n'
              '    <span class="work">%s・%s</span>\n'
              '    <span class="src">%s</span>\n  </div>\n'
              '  <a class="back" href="%s-drill.html">練習 →</a>\n'
              % (star(w['id']), e(w['title']), e(w['work']), e(w['chapter']),
                 e(w['range']), e(w['id']))
            + CONTROLS + '</header>\n\n' + PANEL
            + '\n<script src="%s"></script>\n' % ver('assets/kit.js')
            + '<script src="%s"></script>\n' % ver('assets/works.js')
            + '<script src="%s"></script>\n' % ver('assets/favorites.js')
            + '<script src="%s"></script>\n' % ver('assets/spots.js')
            + '<script src="%s"></script>\n' % ver('assets/lexicon.js')
            + '<script src="%s"></script>\n' % ver('assets/conj.js')
            + '<script src="texts/%s"></script>\n' % w['file']
            + '<script src="%s"></script>\n' % ver('assets/why.js')
            + '<script src="%s"></script>\n' % ver('assets/reader.js')
            + '<script src="%s"></script>\n' % ver('assets/zoom.js')
            + '<script src="%s"></script>\n</body>\n</html>\n' % ver('assets/pdf.js'))


def drill_page(w):
    return (head('%s 練習｜%s — 古文リーダー' % (w['title'], w['work']),
                 '%s『%s』の重要語フラッシュカード・単語クイズ・文法問題。' % (w['work'], w['title']), 'drill')
            + '<header>\n'
              '  <a class="back" href="%s.html">← 本文へ</a>\n'
              '  %s\n'
              '  <div class="brand">\n    <h1>%s</h1>\n'
              '    <span class="work">%s・練習</span>\n  </div>\n'
              '  <a class="back" href="index.html">作品一覧</a>\n</header>\n\n'
              % (e(w['id']), star(w['id']), e(w['title']), e(w['work']))
            + '<div class="drill-wrap">\n'
              '  <div class="drill-tabs" role="tablist">\n'
              '    <button role="tab" id="tab-spot" aria-selected="true">テスト対策</button>\n'
              '    <button role="tab" id="tab-card" aria-selected="false">フラッシュカード</button>\n'
              '    <button role="tab" id="tab-vocab" aria-selected="false">単語クイズ</button>\n'
              '    <button role="tab" id="tab-quiz" aria-selected="false">文法問題</button>\n'
              '  </div>\n'
              '  <p class="drill-note">テストでねらわれやすい <b id="spot-size">0</b> 箇所の一問一答と、'
              '品詞分解から自動で作った カード <b id="deck-size">0</b> 枚・'
              '単語クイズの対象語 <b id="vocab-size">0</b> 語。'
              'クイズは毎回10問を選び直します。覚えた記録はこの端末のブラウザに残ります。</p>\n'
              '  <div class="scope" id="scope" role="group" aria-label="出題の範囲">\n'
              '    <button data-scope="all" aria-pressed="true">すべての語</button>\n'
              '    <button data-scope="imp" aria-pressed="false">要チェックのみ</button>\n'
              '  </div>\n'
              '  <div class="pane-d" id="pane-spot"><div id="spot-box"></div></div>\n'
              '  <div class="pane-d" id="pane-card" hidden>\n'
              '    <div class="bar" id="card-bar"></div>\n'
              '    <div class="stat" id="card-stat"></div>\n'
              '    <div id="card-box"></div>\n'
              '  </div>\n'
              '  <div class="pane-d" id="pane-vocab" hidden><div id="vocab-box"></div></div>\n'
              '  <div class="pane-d" id="pane-quiz" hidden><div id="quiz-box"></div></div>\n'
              '</div>\n'
            + '\n<script src="%s"></script>\n' % ver('assets/kit.js')
            + '<script src="%s"></script>\n' % ver('assets/works.js')
            + '<script src="%s"></script>\n' % ver('assets/favorites.js')
            + '<script src="%s"></script>\n' % ver('assets/spots.js')
            + '<script src="%s"></script>\n' % ver('assets/lexicon.js')
            + '<script src="%s"></script>\n' % ver('assets/conj.js')
            + '<script src="texts/%s"></script>\n' % w['file']
            + '<script src="%s"></script>\n' % ver('assets/why.js')
            + '<script src="%s"></script>\n</body>\n</html>\n' % ver('assets/drill.js'))


def card(w):
    return ('    <a class="card" href="%s.html" data-id="%s">\n'
            '      %s\n'
            '      <span class="spine">%s</span>\n'
            '      <span class="meat">\n        <h3>%s</h3>\n'
            '        <span class="by">%s／%s</span>\n'
            '        <p class="lede">%s</p>\n'
            '        <span class="stats"><span>%s</span><span>%d語</span>'
            '<span class="aux">助動詞%d</span></span>\n'
            '      </span>\n    </a>\n'
            % (e(w['id']), e(w['id']), star(w['id']), e(w['work']), e(w['title']),
               e(w['author']), e(w['era']), e(w['lede']), e(w['chapter']),
               w['words'], w['aux']))


def index_page(works):
    tot_w = sum(w['words'] for w in works)
    tot_a = sum(w['aux'] for w in works)
    out = [head('古文リーダー',
                '古文・漢文の名文を縦書きで読み、語をクリックすると品詞・活用・意味が引ける学習サイト。',
                'home'),
           '<div class="home-wrap">\n<div class="hero">\n'
           '  <p class="eyebrow">縦書きで読む・語をひらいて確かめる</p>\n'
           '  <h1>古文リーダー</h1>\n'
           '  <p>教科書でおなじみの章段を、原文のまま縦書きで並べました。'
           '語をクリックすると品詞・活用の種類と活用形・意味が出ます。'
           '助動詞だけを浮かび上がらせたり、敬語に圏点を打ったり、現代語訳を隣に立てたりしながら読み進められます。'
           '章段ごとにフラッシュカードと確認問題も用意しました。</p>\n'
           '  <div class="counts">\n    <div><b>%d</b>章段</div>\n    <div><b>%d</b>作品</div>\n'
           '    <div><b>%s</b>語を品詞分解</div>\n    <div><b>%s</b>語の助動詞</div>\n  </div>\n</div>\n'
           % (len(works), len({w['work'] for w in works}), format(tot_w, ','), format(tot_a, ',')),
           '<section class="genre shelf">\n'
           '  <h2>お気に入り<span class="n" id="fav-count">0</span></h2>\n'
           '  <div class="cards" id="fav-cards" hidden></div>\n'
           '  <div class="fav-empty" id="fav-empty" hidden>'
           'カードの<button class="star" aria-pressed="true" tabindex="-1">★</button>'
           'を押すと、ここによく読む章段が並びます。</div>\n</section>\n']
    seen = set()
    for label, genres in GROUPS:
        items = [w for w in works if w['genre'] in genres]
        if not items:
            continue
        seen |= {w['id'] for w in items}
        out.append('<section class="genre">\n  <h2>%s</h2>\n  <div class="cards">\n' % e(label))
        out += [card(w) for w in items]
        out.append('  </div>\n</section>\n')
    missing = [w for w in works if w['id'] not in seen]
    if missing:
        raise SystemExit('ジャンル未分類: %s' % ', '.join(w['id'] for w in missing))
    out.append('<div class="home-foot">\n'
               '  本文は著作権の切れた古典作品。品詞分解・現代語訳・語法メモは学校文法（古典文法）に沿って書き起こしたものです。<br>\n'
               '  お気に入りと学習の記録は、この端末のブラウザにだけ保存されます。<br>\n'
               '  章段を足すときは <code>texts/</code> に .js を置いて <code>python3 build.py</code> を実行してください。\n'
               '</div>\n</div>\n'
               '<script src="%s"></script>\n' % ver('assets/works.js') +
               '<script src="%s"></script>\n' % ver('assets/favorites.js') +
               '<script src="%s"></script>\n</body>\n</html>\n' % ver('assets/index.js'))
    return ''.join(out)


def load_en():
    """英語の教材。公開ビルドには含めないので、手元にあるときだけ読み込む。"""
    out = []
    for d in ('eigo/private', 'eigo/texts'):
        for path in sorted((ROOT / d).glob('*.js')) if (ROOT / d).exists() else []:
            src = path.read_text(encoding='utf-8')
            w = {'file': path.name, 'dir': d}
            for key in ('id', 'work', 'title', 'chapter', 'lede', 'hint', 'publisher'):
                m = re.search(r"\n?\s*%s\s*:\s*'((?:[^'\\]|\\.)*)'" % key, src)
                w[key] = m.group(1) if m else ''
            if not w['id']:
                continue
            w['sents'] = len(re.findall(r"\n    S\(", src))
            w['words'] = len(re.findall(r"\n    V\(", src))
            out.append(w)
    return out


EN_CONTROLS = '''  <div class="tools">
    <div class="grp">
      <button class="chip plain" id="slashBtn" aria-pressed="true">区切り線</button>
      <button class="chip plain" id="cjaBtn" aria-pressed="false">区切りごとの訳</button>
      <button class="chip plain" id="jaBtn" aria-pressed="false">全文訳</button>
      <button class="chip plain" id="noteBtn" aria-pressed="true">構文メモ</button>
    </div>
    <div class="grp"><span class="lab" id="encount"></span></div>
  </div>
'''


def en_work_page(w):
    return (head('%s｜%s' % (w['title'], w['work']), w['lede'], 'en')
            + '<header>\n  <a class="back" href="index.html">← 英語の一覧</a>\n'
              '  <div class="brand">\n    <h1>%s</h1>\n'
              '    <span class="work">%s</span>\n    <span class="src">%s</span>\n  </div>\n'
              % (e(w['title']), e(w['work']), e(w['chapter']))
            + EN_CONTROLS + '</header>\n'
            + '<div class="en-wrap">\n  <div id="enbody"></div>\n'
              '  <aside class="enpanel" id="enpane"></aside>\n</div>\n'
            + '<script src="%s"></script>\n' % ver('assets/enkit.js')
            + '<script src="%s/%s"></script>\n' % (w['dir'].split('/')[1], w['file'])
            + '<script src="%s"></script>\n</body>\n</html>\n' % ver('assets/en-reader.js'))


def en_index_page(ws):
    cards = ''.join(
        '    <a class="card" href="%s.html">\n      <span class="spine">%s</span>\n'
        '      <span class="meat">\n        <h3>%s</h3>\n'
        '        <span class="by">%s</span>\n        <p class="lede">%s</p>\n'
        '        <span class="stats"><span>%s</span><span>%d文</span>'
        '<span class="aux">新出語%d</span></span>\n      </span>\n    </a>\n'
        % (e(w['id']), e(w['publisher'] or '教材'), e(w['title']), e(w['work']),
           e(w['lede']), e(w['chapter']), w['sents'], w['words']) for w in ws)
    return (head('英語｜' + SITE, '英文を意味のまとまりで読む。', 'home')
            + '<div class="home-wrap">\n<div class="hero">\n'
              '  <p class="eyebrow"><a href="../index.html">← 教科の一覧</a></p>\n'
              '  <h1>英語</h1>\n'
              '  <p>英文を意味のまとまりごとに区切って読みます。区切りをクリックするとその訳が出ます。'
              '全文訳・構文メモ・新出語は上のボタンで切り替えられます。</p>\n</div>\n'
            + ('<section class="genre"><h2>教材</h2>\n<div class="cards">\n%s</div>\n</section>\n' % cards
               if ws else '<p class="lede">まだ教材がありません。</p>\n')
            + '<div class="home-foot">教科書の本文を含むため、このページと教材は'
              '<b>非公開のリポジトリと自分の端末の中だけ</b>にあります。公開サイトには出ていません。</div>\n'
            + '</div>\n</body>\n</html>\n')


def hub_page(works, en_n=0):
    open_counts = {'kobun': len(works), 'eigo': en_n}
    cards = []
    # 英語は教科書本文を含むので公開ビルドには入らない。
    # 教材が手元にあるときだけ枠を出し、無いときは枠ごと消す（準備中も出さない）。
    shown = [sb for sb in SUBJECTS if sb['id'] != 'eigo' or en_n]
    for sb in shown:
        n = open_counts.get(sb['id'], 0)
        soon = sb['status'] != 'open' and not n
        inner = (
            '  <span class="sub-icon" aria-hidden="true">%s</span>\n'
            '  <span class="sub-meat">\n'
            '    <span class="sub-name">%s<span class="sub-sub">%s</span></span>\n'
            '    <span class="sub-desc">%s</span>\n'
            '    <span class="sub-stat">%s</span>\n'
            '  </span>\n'
            % (sb['icon'], e(sb['name']), e(sb['sub']), e(sb['desc']),
               ('%d 章段' % n if sb['id'] == 'kobun' else '%d 課' % n) if not soon else '準備中'))
        if soon:
            cards.append('<div class="subcard soon" aria-disabled="true">\n%s</div>\n' % inner)
        else:
            cards.append('<a class="subcard" href="%s/index.html">\n%s</a>\n' % (sb['id'], inner))
    return (head(SITE, SITE_DESC, 'home hub')
            + '<div class="home-wrap">\n'
              '<div class="hero">\n'
              '  <p class="eyebrow">原典にあたって、自分の手で確かめる</p>\n'
              '  <h1>%s</h1>\n'
              '  <p>教科書に載っている文章を、そのままの形で読みながら、'
              'わからない語をその場でひらいて確かめられるようにした学習サイトです。'
              '登録も課金もありません。</p>\n'
              '</div>\n'
              '<section class="genre"><h2>教科</h2>\n<div class="subcards">\n%s</div>\n</section>\n'
              % (e(SITE), ''.join(cards))
            + foot() + '</div>\n</body>\n</html>\n')


DOCS = {}          # 法務ページの本文は docs/*.html から読む


def doc_page(slug, title, desc):
    body = (ROOT / 'docs' / (slug + '.html')).read_text(encoding='utf-8')
    body = body.replace('__CONTACT__', CONTACT)
    return (head(title + '｜' + SITE, desc, 'home doc')
            + '<div class="home-wrap">\n<article class="legal">\n'
            + body
            + '</article>\n' + foot() + '</div>\n</body>\n</html>\n')


def main():
    global PAGE_DIR
    works = load()
    favs = [w['id'] for w in works if w['work'] in DEFAULT_FAV_WORKS]

    PAGE_DIR = 'kobun'
    sub = ROOT / 'kobun'
    sub.mkdir(exist_ok=True)
    for w in works:
        (sub / (w['id'] + '.html')).write_text(work_page(w), encoding='utf-8')
        (sub / (w['id'] + '-drill.html')).write_text(drill_page(w), encoding='utf-8')
    (ROOT / 'assets' / 'works.js').write_text(
        'window.WORKS = [\n' + ''.join(
            "  {id:'%s', work:'%s', title:'%s'},\n" % (w['id'], w['work'], w['title'])
            for w in works) + '];\n'
        + 'window.DEFAULT_FAVORITES = ' + repr(favs).replace('"', "'") + ';\n',
        encoding='utf-8')
    (sub / 'index.html').write_text(index_page(works), encoding='utf-8')

    en = load_en()
    if en:
        PAGE_DIR = 'eigo'
        for w in en:
            (ROOT / 'eigo' / (w['id'] + '.html')).write_text(en_work_page(w), encoding='utf-8')
        (ROOT / 'eigo' / 'index.html').write_text(en_index_page(en), encoding='utf-8')

    PAGE_DIR = ''
    (ROOT / 'index.html').write_text(hub_page(works, len(en)), encoding='utf-8')
    for slug, title, desc in [
        ('privacy',  'プライバシーポリシー', 'このサイトが集める情報と、その扱いについて。'),
        ('terms',    '利用規約',            'このサイトを使うときの約束ごと。'),
        ('cookies',  'Cookie とデータの扱い', 'Cookie を使っていないことと、端末に保存する内容について。'),
        ('404',      'ページが見つかりません', 'お探しのページは移動したか、無くなっています。')]:
        if (ROOT / 'docs' / (slug + '.html')).exists():
            (ROOT / (slug + '.html')).write_text(doc_page(slug, title, desc), encoding='utf-8')

    print('%d 章段 / %d 語　（教科ページ %d 枚）'
          % (len(works), sum(w['words'] for w in works), len(works) * 2 + 1))
    print('既定のお気に入り: %s' % ', '.join(favs))
    if en:
        print('英語（手元だけ）: %s' % ', '.join('%s（%d文・%d語）' % (w['title'], w['sents'], w['words']) for w in en))


if __name__ == '__main__':
    main()
