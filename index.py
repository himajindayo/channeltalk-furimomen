import channel
import random
import time

CHANNEL_ID = "240996"
ITRSA_GROUP_ID = "574628"
ROSHIRO_GROUP_ID = "574642"
FURIMOMEN_GROUP_ID = "576454"

omikuji = ["<b>小吉だ！ラッキーアイテムはフリモメシだぞ！</b>","<b>末吉だ！まあまあ、むしろいいことがあるかもだぜ　俺に。</b>","<b>大吉だぞ！おめでとう☺️</b>","<b>凶だと…！？俺が味方でよかったな、ブラザー！</b>","<b>だ、大凶……大丈夫だ、問題ない！</b>"]

all =["<b>呼ばれてないけど飛び出たフリーモーションメーーン！！</b>",
    "<b>報酬はスイス銀行に振り込んでくれ</b>",
    "<b>俺の手にかかればFlash作成も赤子の手をひねる極悪さだから<br>俺は赤子の手はひねらない！</b>",
    "<b>まあまあ、その方が楽しいかもしれないぜ　俺が。</b>",
    "<b>理系の俺様的には超ウラン元素であるメンデレビウムの印象が強いな。</b>",
    "<b>…やべぇ、ほんまもんだコイツ！</b>",
    "<b>お駄賃くれ</b>",
    "<b>とにかく俺と一緒にFlash作成の深さを理解するのだ！答はイエスorはいだ！！</b>",
    "<b>アキバは深いな</b>",
    "<b>…そろそろツッコまれる気がするぞ！</b>",
    "<b>のび太くん宿題は終わったのかい!?</b>",
    "<b>【SSR】俺とタオルの人、2人の力を合わせて刑法を最初のページから順番に違反していくぞ！</b>",
    "<b>おっと、警察には通報しないでくれ</b>",
    "<b>おっと、声が良すぎたみたいだな！</b>",
    "<b>お巡りさん、俺です！</b>",
    "<b>Flashは死んでなんかいない！俺達の心のなかで生きているんだ！！</b>",
    "<b>Flashを知らないなんて遅れてるぞ？</b>",
    "<b>逮捕！</b>",
    "<b>お前は今までに洗濯したターコイズブルータイツの枚数を覚えているか？</b>",
    "<b>ギターは任せてくれ。知り合いの金髪ちゃんがプロなんだ</b>",
    "<b>このわざとらしいターコイズブルー！</b>",
    "<b>この戦いが終わったら、ツイートするんだ…</b>",
    "<b>これが兄弟愛！</b>",
    "<b>そのキレイな顔をぶっ飛ばしてやるぜ</b>",
    "<b>魔法少女に変身だ！</b>",
    "<b>いつもあなたのそばに。振り向けばフリモメン。</b>",
    "<b>おめでとう︕今⽇から君はフリモメンだ︕</b>",
    "<b>さあよいこのみんな︕フリモメンしような︕</b>",
    "<b>君もフリモメンになるんだよ︕</b>",
    "<b>どうも、弦巻マキです</b>",
    "<b>代わりにヨーグルト食べておいたよ。</b>",
    "<b>なるほど…。トド岩送りだ！！</b>",
    "<b>可愛いフリモメンかと思った︖残念︕小春六花ちゃんでした︕</b>",
    "<b>北海道で全身タイツは流⽯にまずったな…</b>",
    "<b>魔女っ子フリモたん登っ場～！</b>",
    "<b>働きたくない！！！</b>",
    "<b>おや？間違ったかな？お兄ちゃんだからな！</b>",
    "<b>迷えるFlash職人見習いのつよーい味方、フリモです☆</b>",
    "<b>どうしてこんなになるまで放っておいたんだ　おい！</b>",
    "<b>世の中何でも美少女が出ればいいとか思うなってコトさ。</b>",
    "<b>こんなところにいられるか！俺は部屋に戻らせてもらう！</b>",
     "<b>･･･まー、よく考えたら俺ら、 ビジネスソフト扱いだから関係ないかー</b>",
    "<b>まあまあちょっと最初にキャラの立ち具合について話しあおうぜ！</b>",
     "<b>あーもう面倒くさいなー</b>",
    "<b>おおっと 具体的な商標名を言うとややこしくなるから穏やかに頼むぜ</b>",
    "<b>恋する力で可憐に咲くんだぜ</b>"]

while True:
    try:
        ITRSA_body = channel.get_message(CHANNEL_ID,ITRSA_GROUP_ID)
        print(ITRSA_body)
        # time.sleep(1)
        if ITRSA_body == "/goroku":
            goroku = random.choice(all)
            channel.send_test_message(goroku,CHANNEL_ID,ITRSA_GROUP_ID)
        if ITRSA_body == "/おみくじ":
            omikuji_kekka = random.choice(omikuji)
            channel.send_test_message(omikuji_kekka,CHANNEL_ID,ITRSA_GROUP_ID)
        ROSHIRO_body = channel.get_message(CHANNEL_ID,ROSHIRO_GROUP_ID)
        print(ROSHIRO_body)
        # time.sleep(1)
        if ROSHIRO_body == "/goroku":
            goroku = random.choice(all)
            channel.send_test_message(goroku,CHANNEL_ID,ROSHIRO_GROUP_ID)

        FURIMOMEN_body = channel.get_message(CHANNEL_ID,FURIMOMEN_GROUP_ID)
        print(FURIMOMEN_body)
        # time.sleep(1)
        if FURIMOMEN_body == "/goroku":
            goroku = random.choice(all)
            channel.send_test_message(goroku,CHANNEL_ID,FURIMOMEN_GROUP_ID)

    except Exception as e:
        print(e)