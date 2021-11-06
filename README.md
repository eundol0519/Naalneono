# 항해99 미니 프로젝트1 6조
***
## 팀원 & 제작기간
***
오은희 / 김주영 / 정민수 / 한동훈

제작기간 : 2021.11.01 ~ 11.05

## 프로젝트
***
### 1. 나알너노
나만 혼자 듣기 아까운 노래를 리뷰함으로써 다른 사람들과 공유하고 소통 할 수 있는 사이트<br>

### 2. 와이어프레임
![와이어프레임](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7573ea10-97f2-4832-a968-7bae82670cec/1111.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20211106%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20211106T005716Z&X-Amz-Expires=86400&X-Amz-Signature=639e236c572dda85011005f7a55d269d3bff1761bf340f181bd3085eab1d477b&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%221111.jpg%22 "와이어프레임")

### 3. 링크
http://3.34.255.221/

### 4. API
|기능|Method|URL|request|response|
|------|---|---|---|---|
|로그인|POST|/api/main|{id_give':userid, 'm_pwd_give':userpw}|token|
|회원가입|POST|/api/join|{'m_name':m_name, 'm_id':m_id, 'm_pwd':m_pwd}||
|닉네임 중복확인|POST|/api/nameCheck|{"m_name_give": userName}|닉네임 중복 여부|
|아이디 중복확인|POST|/api/idCheck|{'m_id_give': userId}|아이디 중복 여부|
|리뷰 게시물 작성|POST|/api/reviewWrite|{'music_url': url,'review_give': review}|리뷰 중복 작성 여부, 리뷰 등록 여부|
|리뷰 게시물 수정|POST|/api/reviewUpdate|{'rv_singer_give': rvSinger, 'rv_song_give': rvSong,'review_update': reUpdate}|리뷰 수정 여부|
|리뷰 게시물 임시저장|POST|/api/tempSave|{'music_url': url, 'review_give': review}|임시저장 중복 여부|
|좋아요|POST|/api/like|{'rv_singer_give': rv_singer, rv_song_give: rv_song}||
|리뷰 삭제|POST|/api/delete|{'rv_singer_give': rv_singer, 'rv_song_give': rv_song}|삭제 완료 여부|
|댓글 작성|POST|/api/commentSubmit|{'rv_comment_give':inputText, 'rv_singer_give':rv_singer, 'rv_song_give':rv_song}||
|팝업에 댓글 불러오기|GET|/api/popUp|{'rvSingerGive':rv_singer,'rvSongGive':rv_song}||

### 5. 기술스택

__*BackEnd*__
- Python
- Flask
- MongoDB

__*FrontEnd*__
- HTML
- CSS
- Javascript
- jQuery

__*Hosting*__
- AWS : EC2
- Ubuntu

### 6. 해결한 문제
* 클라이언트에서 요청한 데이터를 서버에서 리턴할때 요청했던 페이지가 아니라 다른 페이지로 보냈어야 하는 문제.
→ 서버로 요청을 보내지 않고 url(location.href)로 데이터 전달.

### 7. 궁금한 점
* merge 할 때 충돌을 줄이는 방법
* 좋아요 기능을 구현하다가 회원마다 한번만 누를 수 있게 하는 부분을 고려하지 않아 무한으로 누를 수 있게 구현을 했는 데 처음 프로젝트를 구상 할 때 이런 문제를 고려 할 수 있는 방법 
* jinja2에서 if문이나 for문 기능을 script 부분에서 temp_html로 html을 구현한 경우 사용 할 수 있는 지 
* 기능구현 하기가 너무 어려운데 구현하기전 생각하면 좋은 것