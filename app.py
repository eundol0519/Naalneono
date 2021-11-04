import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

SECRET_KEY = 'SPARTA'

app = Flask(__name__)

# Mongo DB 연결
from pymongo import MongoClient
# client = MongoClient('내AWS아이피', 27017, username="test", password="test")
client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week3

## HTML을 주는 부분을 꼭 해야 한다.
@app.route('/')
def home():
   return render_template('main.html')

## HTML을 주는 부분을 꼭 해야 한다.
@app.route('/join')
def join():
    return render_template('join.html')

@app.route('/review')
def review():
    reviews = list(db.reviews.find({}, {'_id': False}))
    return render_template('review.html', reviews=reviews)

## reviewWrite.html
@app.route('/reviewWrite')
def reviewWirte():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        tempSave = db.tempurl.find_one({'m_id': payload['id']}, {'_id': False})
        return render_template('reviewWrite.html', tempSave=tempSave)
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

## reviewUpdate.html
@app.route('/reviewUpdate')
def reviewUpdate():
    return render_template('reviewUpdate.html')

## 닉네임 중복확인
@app.route('/api/nameCheck', methods=["POST"])
def name_Check():
    m_name_receive = request.form['m_name_give']
    exists = bool(db.member_info.find_one({"m_name":m_name_receive}))
    return jsonify({'result':'success', 'exists':exists})

## 아이디 중복확인
@app.route('/api/idCheck', methods=['POST'])
def id_Check():
    m_id_receive = request.form['m_id_give']
    exists = bool(db.member_info.find_one({"m_id": m_id_receive}))
    return jsonify({'result': 'success', 'exists': exists})

## 회원가입
@app.route('/api/join', methods=['POST'])
def member_join():
    m_name_receive = request.form['m_name_give']
    m_id_receive = request.form['m_id_give']
    m_pw_receive = request.form['m_pw_give']
    password_hash = hashlib.sha256(m_pw_receive.encode('utf-8')).hexdigest()
    doc = {
        "m_name" : m_name_receive,   # 닉네임
        "m_id": m_id_receive,    # 아이디
        "m_pw": password_hash,     # 비밀번호
    }
    db.member_info.insert_one(doc)
    return jsonify({'result': 'success'})

## 로그인
@app.route('/api/login', methods=['POST'])
def login():
    m_id_receive = request.form['m_id_give']
    m_pw_receive = request.form['m_pw_give']

    pw_hash = hashlib.sha256(m_pw_receive.encode('utf-8')).hexdigest()
    result = db.member_info.find_one({'m_id': m_id_receive, 'm_pw': pw_hash})

    if result is not None:
        payload = {
         'id': m_id_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(token)
        # jwt 토큰은 놀이공원 자유이용권 같은 거

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

## API 역할을 하는 부분

## reviewWrite api
## crawling 후 DB 저장.
@app.route('/api/reviewWrite', methods=['POST'])
def write_review():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        url_receive = request.form['music_url']
        rv_review = request.form['review_give']
        m_id = payload['id']

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url_receive, headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')
        rv_song = soup.select_one(
            '#frm > div > table > tbody > tr > td:nth-child(4) > div > div > div:nth-child(1) > span > a').text
        rv_image = soup.select_one('#d_album_org > img')['src']
        rv_singer = soup.select_one(
            '#frm > div > table > tbody > tr > td:nth-child(4) > div > div > div.ellipsis.rank02 > a').text

        ## 리뷰 등록 중복 체크
        dup_check = db.reviews.find_one({'rv_song': rv_song})
        if dup_check is not None:
            db.tempurl.delete_one({'m_id': m_id, 'rv_url': url_receive})
            return jsonify({'msg': '이미 리뷰가 등록된 노래 입니다.'})
        else:
            doc = {'rv_song': rv_song, 'rv_image': rv_image, 'rv_singer': rv_singer, 'rv_url': url_receive,
                   'rv_review': rv_review, 'rv_like': '0', 'rv_comment': ''}
            db.reviews.insert_one(doc)
            db.tempurl.delete_one({'m_id': m_id, 'rv_url': url_receive})
            return jsonify({'msg': '저장 완료.'})

    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


@app.route('/api/reviewUpdate', methods=['POST'])
def review_update():
    rv_singer = request.form['rv_singer_give']
    rv_review = request.form['review_update']
    rv_song = request.form['rv_song_give']
    db.reviews.update_one({'rv_singer':rv_singer, 'rv_song':rv_song},{'$set':{'rv_review':rv_review}})
    return jsonify({'msg': '야호'})

@app.route('/api/tempSave', methods=['POST'])
def temp_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        rv_url = request.form['music_url']
        rv_review = request.form['review_give']
        doc = {'rv_url': rv_url, 'rv_review': rv_review, 'm_id': payload['id']}
        db.tempurl.insert_one(doc)
        return jsonify({'msg': '임시저장 완료'})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# @app.route('/api/tempWrite', methods=['GET'])
# def temp_write():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         tempSave = db.tempurl.find_one({'m_id': payload['id']},{'_id': False})
#         return jsonify({'tempSave': tempSave})
#     except jwt.ExpiredSignatureError:
#         # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
#         return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
#     except jwt.exceptions.DecodeError:
#         return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})




## 좋아요 api
## POST 방식으로 rv_singer_give 를 받아옴.
@app.route('/api/like', methods=['POST'])
def like_up():
    singer_receive = request.form['rv_singer_give']
    song_receive = request.form['rv_song_give']
    music_singer = db.reviews.find_one({'rv_singer': singer_receive, 'rv_song': song_receive})
    current_like = music_singer['rv_like']
    new_like = int(current_like) + 1
    db.reviews.update_one({'rv_singer': singer_receive, 'rv_song': song_receive}, {'$set': {'rv_like': new_like}})
    return jsonify({'msg' : '좋아요 완료'})

## 삭제 api
@app.route('/api/delete', methods=['POST'])
def delete_pop():
    singer_receive = request.form['rv_singer_give']
    song_receive = request.form['rv_song_give']
    db.reviews.delete_one({'rv_singer': singer_receive, 'rv_song': song_receive})
    return jsonify({'msg' : '삭제 완료'})

@app.route('/api/commentSubmit', methods=['POST'])
def commentSubmit():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        comment_receive = request.form['rv_comment_give']
        singer_receive = request.form['rv_singer_give']
        song_receive = request.form['rv_song_give']
        userinfo = db.member_info.find_one({'m_id': payload['id']}, {'_id': False})
        m_nick = userinfo['m_name']

        doc = {
            'rv_comment': comment_receive,
            'rv_singer': singer_receive,
            'rv_song': song_receive,
            'm_name': m_nick
            }
        db.comments.insert_one(doc)
        return jsonify({'msg' :'댓글작성 완료'})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


## 팝업창 api
## GET 방식으로 rvSingerGive 를 받아옴
@app.route('/api/popUp', methods=['GET'])
def pop_up():
    singer_receive = request.args.get('rvSingerGive')
    song_receive = request.args.get('rvSongGive')
    musicSinger = db.reviews.find_one({'rv_singer': singer_receive, 'rv_song': song_receive },{'_id':False})
    return jsonify({'musicSinger': musicSinger})

@app.route('/api/commentUp', methods=['GET'])
def comment_up():
     singer_receive = request.args.get('rvSingerGive')
     song_receive = request.args.get('rvSongGive')
     comments = list(db.comments.find({'rv_singer': singer_receive, 'rv_song': song_receive},
                                         {'_id': False, 'rv_singer': False, 'rv_song': False}))
     return jsonify({'comments': comments})




if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)