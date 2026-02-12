"""
🐟 블로그 자동화 프로그램 - 웹 대시보드
Flask 기반 웹 인터페이스입니다.
누구나 자신의 네이버 아이디/비밀번호를 입력하면 사용할 수 있습니다!
"""

import os
import sys
import secrets

# 프로젝트 루트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify
)
from src.database import DatabaseManager
from src.posting.scheduler import get_scheduler
from config.settings import NaverConfig, APIConfig

# ============================================
# Flask 앱 초기화
# ============================================
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "kodari-blog-auto-secret-2026-stable")
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24시간

# 데이터베이스 & 스케줄러
db = DatabaseManager()
scheduler = get_scheduler()
scheduler.start()


# ============================================
# 헬퍼 함수
# ============================================
def login_required(f):
    """로그인 필수 데코레이터"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('naver_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_user_id():
    """현재 로그인된 사용자 ID"""
    return session.get('naver_id', '')


def get_content_generator():
    """AI 콘텐츠 생성기 (사용자별 API 키 적용)"""
    from config.settings import APIConfig
    from src.content.generator import ContentGenerator

    # 사용자가 로그인 시 입력한 API 키가 있으면 직접 전달
    user_api_key = session.get('ai_api_key', '')
    user_provider = session.get('ai_provider', '')

    # API 키 형식으로 프로바이더 자동 감지 (안전장치)
    if user_api_key:
        if user_api_key.startswith('AIza') and user_provider != 'gemini':
            print(f"🔄 API 키 형식이 Google이므로 프로바이더를 gemini로 자동 변경")
            user_provider = 'gemini'
        elif user_api_key.startswith('sk-') and user_provider != 'openai':
            print(f"🔄 API 키 형식이 OpenAI이므로 프로바이더를 openai로 자동 변경")
            user_provider = 'openai'

    # 프로바이더가 없으면 설정에서 가져오기
    if not user_provider:
        user_provider = APIConfig.AI_PROVIDER

    print(f"🔑 AI 생성기 초기화: provider={user_provider}, key={'***'+user_api_key[-4:] if user_api_key else 'None'}")

    # ContentGenerator에 직접 키와 프로바이더를 전달
    return ContentGenerator(provider=user_provider, api_key=user_api_key or None)


# ============================================
# 자동 로그인 헬퍼
# ============================================
def auto_login_from_env():
    """서버 시작 시 .env의 네이버 계정 정보로 자동 로그인"""
    naver_id = NaverConfig.ID
    naver_pw = NaverConfig.PASSWORD
    blog_id = NaverConfig.BLOG_ID or naver_id
    ai_provider = APIConfig.AI_PROVIDER

    # Gemini 키가 있으면 Gemini, OpenAI 키가 있으면 OpenAI
    ai_api_key = ''
    if ai_provider == 'gemini' and APIConfig.GEMINI_API_KEY:
        ai_api_key = APIConfig.GEMINI_API_KEY
    elif APIConfig.OPENAI_API_KEY:
        ai_api_key = APIConfig.OPENAI_API_KEY
    elif APIConfig.GEMINI_API_KEY:
        ai_api_key = APIConfig.GEMINI_API_KEY

    if naver_id and naver_pw:
        session.permanent = True
        session['naver_id'] = naver_id
        session['naver_pw'] = naver_pw
        session['blog_id'] = blog_id
        session['ai_provider'] = ai_provider
        if ai_api_key:
            session['ai_api_key'] = ai_api_key

        # 스케줄러에 인증정보 등록
        scheduler.set_user_credentials(naver_id, naver_pw, blog_id)
        return True
    return False


# ============================================
# 라우트: 인증
# ============================================
@app.route('/')
def index():
    if session.get('naver_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        naver_id = request.form.get('naver_id', '').strip()
        naver_pw = request.form.get('naver_pw', '').strip()
        blog_id = request.form.get('blog_id', '').strip() or naver_id
        ai_provider = request.form.get('ai_provider', 'openai')
        ai_api_key = request.form.get('ai_api_key', '').strip()

        if not naver_id or not naver_pw:
            flash('네이버 아이디와 비밀번호를 입력해주세요.', 'error')
            return render_template('login.html',
                                   env_naver_id=NaverConfig.ID,
                                   env_blog_id=NaverConfig.BLOG_ID,
                                   env_ai_provider=APIConfig.AI_PROVIDER)

        # 세션에 저장 (비밀번호는 메모리에만)
        session.permanent = True
        session['naver_id'] = naver_id
        session['naver_pw'] = naver_pw
        session['blog_id'] = blog_id
        session['ai_provider'] = ai_provider
        if ai_api_key:
            session['ai_api_key'] = ai_api_key

        # 스케줄러에 인증정보 등록
        scheduler.set_user_credentials(naver_id, naver_pw, blog_id)

        flash(f'환영합니다, {naver_id}님! 🐟', 'success')
        return redirect(url_for('dashboard'))

    # GET 요청: .env에 계정 정보가 있으면 자동 로그인
    if not session.get('naver_id') and NaverConfig.ID and NaverConfig.PASSWORD:
        if auto_login_from_env():
            flash(f'✅ .env 설정으로 자동 로그인되었습니다! ({NaverConfig.ID}님)', 'success')
            return redirect(url_for('dashboard'))

    # 자동 로그인 실패 또는 .env 없으면 로그인 폼 표시 (기본값 미리 채움)
    return render_template('login.html',
                           env_naver_id=NaverConfig.ID,
                           env_blog_id=NaverConfig.BLOG_ID,
                           env_ai_provider=APIConfig.AI_PROVIDER)


@app.route('/logout')
def logout():
    user_id = get_user_id()
    if user_id:
        scheduler.remove_user_credentials(user_id)
    session.clear()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('login'))


# ============================================
# 라우트: 대시보드
# ============================================
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = get_user_id()
    stats = db.get_stats(user_id)
    drafts = db.get_drafts(user_id)
    scheduled = db.get_scheduled_posts(user_id)
    history_list = db.get_history(user_id, limit=5)

    return render_template('dashboard.html',
                           stats=stats,
                           drafts=drafts,
                           scheduled=scheduled,
                           history_list=history_list)


# ============================================
# 라우트: 글 생성
# ============================================
@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    result = None
    scores = None

    if request.method == 'POST':
        topic = request.form.get('topic', '')
        keyword = request.form.get('keyword', '')
        persona = request.form.get('persona', 'lifestyle_blogger')
        humanize = request.form.get('humanize', '0') == '1'

        if not topic or not keyword:
            flash('주제와 키워드를 입력해주세요.', 'error')
            return render_template('generate.html')

        try:
            # AI 글 생성
            generator = get_content_generator()
            result = generator.generate_blog_post(
                topic=topic,
                keyword=keyword,
                persona=persona
            )

            if result.get('content'):
                # 휴먼터치 적용
                if humanize:
                    from src.content.humanizer import Humanizer
                    humanizer = Humanizer()
                    result['content'] = humanizer.humanize(result['content'])
                    result['content'] = humanizer.add_personal_touch(result['content'], topic)

                # 이미지 자동 삽입
                add_images = request.form.get('add_images', '0') == '1'
                image_source = request.form.get('image_source', 'auto') # 'auto' or 'dalle'
                
                if add_images:
                    try:
                        from src.content.image_manager import ImageManager
                        # OpenAI 키는 환경변수에서 로드됨
                        img_mgr = ImageManager()
                        
                        search_keyword = keyword.split(',')[0].strip()
                        print(f"🖼️ 이미지 검색/생성 시작: 키워드='{search_keyword}', 소스='{image_source}'")
                        
                        # AI 생성일 경우 시간이 더 걸리므로 1장만 생성 (비용 절약)
                        count = 1 if image_source == 'dalle' else 3
                        
                        images = img_mgr.search_images(search_keyword, count=count, source=image_source)
                        
                        if images:
                            result['content'] = img_mgr.insert_images_to_content(
                                result['content'], images, mode="distributed"
                            )
                            result['images'] = images
                            print(f"✅ {len(images)}개 이미지 삽입 완료!")
                        else:
                            print("⚠️ 이미지 검색/생성 결과 없음")
                            
                    except Exception as e:
                        print(f"⚠️ 1차 이미지 검색/생성 실패 ({image_source}): {e}")
                        # 실패 시 무료 이미지(auto)로 재시도
                        if image_source != 'auto':
                            try:
                                print("🔄 무료 이미지(Pexels/Unsplash)로 재시도합니다...")
                                images = img_mgr.search_images(search_keyword, count=3, source="auto")
                                if images:
                                    result['content'] = img_mgr.insert_images_to_content(
                                        result['content'], images, mode="distributed"
                                    )
                                    result['images'] = images
                                    print(f"✅ 무료 이미지 {len(images)}개 대체 삽입 완료!")
                            except Exception as e2:
                                print(f"❌ 이미지 대체 삽입 실패: {e2}")
                        else:
                            # 이미 auto였는데 실패한 경우 -> 플레이스홀더 시도 (search_images('auto')가 이미 함)
                            print("❌ 이미지 삽입 최종 실패.")
                            pass

                # 금칙어 필터링
                from src.content.filter import ContentFilter
                cf = ContentFilter()
                result['content'] = cf.filter_content(result['content'])
                scores = cf.get_content_score(result['content'], keyword)

                flash('✅ 글 생성 완료!', 'success')
            else:
                flash('❌ 글 생성에 실패했습니다. API 키를 확인해주세요.', 'error')
        except Exception as e:
            flash(f'❌ 오류 발생: {str(e)}', 'error')

    return render_template('generate.html', result=result, scores=scores)


# ============================================
# 라우트: 임시저장
# ============================================
@app.route('/drafts')
@login_required
def manage_drafts():
    user_id = get_user_id()
    drafts = db.get_drafts(user_id)
    return render_template('drafts.html', drafts=drafts)


@app.route('/drafts/save', methods=['POST'])
@login_required
def save_draft_from_generate():
    """글 생성 결과를 임시저장"""
    user_id = get_user_id()
    title = request.form.get('title', '제목 없음')
    content = request.form.get('content', '')
    tags_str = request.form.get('tags', '')
    keyword = request.form.get('keyword', '')
    persona = request.form.get('persona', 'lifestyle_blogger')

    tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    draft_id = db.save_draft(user_id, title, content, tags, keyword, persona)
    
    # 네이버 블로그 자동 임시저장 시도
    flash_msg = f'💾 로컬 저장 완료! (ID: {draft_id})'
    flash_type = 'success'
    
    try:
        from src.posting.naver_bot import NaverBlogBot
        bot = NaverBlogBot(
            naver_id=session.get('naver_id'),
            naver_pw=session.get('naver_pw'),
            blog_id=session.get('blog_id')
        )
        # 네이버 블로그 글쓰기 창 열기 및 임시저장
        success = bot.write_post(
            title=title,
            content=content,
            tags=tags,
            mode='draft'
        )
        bot.close()
        
        if success:
            flash_msg += ' + ✅ 네이버 블로그 임시저장 성공!'
        else:
            flash_msg += ' + ⚠️ 네이버 저장 실패 (로그인/브라우저 확인 필요)'
            flash_type = 'warning'
            
    except Exception as e:
        print(f"네이버 자동 저장 실패: {e}")
        flash_msg += f' + ⚠️ 네이버 저장 오류: {e}'
        flash_type = 'warning'

    flash(flash_msg, flash_type)
    return redirect(url_for('manage_drafts'))


@app.route('/drafts/<int:draft_id>')
@login_required
def edit_draft(draft_id):
    user_id = get_user_id()
    draft = db.get_draft(draft_id, user_id)
    if not draft:
        flash('임시저장 글을 찾을 수 없습니다.', 'error')
        return redirect(url_for('manage_drafts'))
    return render_template('edit_draft.html', draft=draft)


@app.route('/drafts/<int:draft_id>/update', methods=['POST'])
@login_required
def update_draft(draft_id):
    user_id = get_user_id()
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    keyword = request.form.get('keyword', '')
    tags_str = request.form.get('tags', '')

    tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    success = db.update_draft(draft_id, user_id, title=title, content=content,
                              tags=tags, keyword=keyword)
    if success:
        flash('💾 저장 완료!', 'success')
    else:
        flash('❌ 저장 실패', 'error')
    return redirect(url_for('edit_draft', draft_id=draft_id))


@app.route('/drafts/<int:draft_id>/delete', methods=['POST'])
@login_required
def delete_draft(draft_id):
    user_id = get_user_id()
    db.delete_draft(draft_id, user_id)
    flash('🗑️ 삭제 완료!', 'success')
    return redirect(url_for('manage_drafts'))


@app.route('/drafts/<int:draft_id>/publish', methods=['POST'])
@login_required
def publish_draft(draft_id):
    """임시저장 글 즉시 발행"""
    user_id = get_user_id()
    draft = db.get_draft(draft_id, user_id)
    if not draft:
        flash('글을 찾을 수 없습니다.', 'error')
        return redirect(url_for('manage_drafts'))

    try:
        from src.posting.naver_bot import NaverBlogBot
        bot = NaverBlogBot(
            naver_id=session.get('naver_id'),
            naver_pw=session.get('naver_pw'),
            blog_id=session.get('blog_id')
        )
        success = bot.write_post(
            title=draft['title'],
            content=draft['content'],
            tags=draft.get('tags', []),
            mode='publish'
        )
        bot.close()

        if success:
            db.add_history(user_id, draft['title'], 'success',
                           content_preview=draft['content'][:200], source='direct')
            # 임시저장 삭제
            db.delete_draft(draft_id, user_id)
            flash('✅ 발행 성공!', 'success')
        else:
            db.add_history(user_id, draft['title'], 'failed', source='direct')
            flash('❌ 발행 실패. 네이버 로그인 상태를 확인해주세요.', 'error')
    except Exception as e:
        flash(f'❌ 발행 오류: {str(e)}', 'error')

    return redirect(url_for('manage_drafts'))


@app.route('/drafts/<int:draft_id>/schedule', methods=['POST'])
@login_required
def schedule_from_draft(draft_id):
    """임시저장 글 발행예약"""
    user_id = get_user_id()
    draft = db.get_draft(draft_id, user_id)
    if not draft:
        flash('글을 찾을 수 없습니다.', 'error')
        return redirect(url_for('manage_drafts'))

    schedule_time = request.form.get('schedule_time', '')
    if not schedule_time:
        flash('예약 시간을 입력해주세요.', 'error')
        return redirect(url_for('edit_draft', draft_id=draft_id))

    db.schedule_post(
        user_id=user_id,
        title=draft['title'],
        content=draft['content'],
        scheduled_time=schedule_time,
        tags=draft.get('tags', []),
        draft_id=draft_id
    )
    flash(f'⏰ 발행 예약 완료! ({schedule_time})', 'success')
    return redirect(url_for('manage_schedule'))


# ============================================
# 라우트: 발행예약 관리
# ============================================
@app.route('/schedule')
@login_required
def manage_schedule():
    user_id = get_user_id()
    scheduled = db.get_scheduled_posts(user_id)
    return render_template('schedule.html', scheduled=scheduled)


@app.route('/schedule/<int:post_id>/cancel', methods=['POST'])
@login_required
def cancel_schedule(post_id):
    user_id = get_user_id()
    success = db.cancel_schedule(post_id, user_id)
    if success:
        flash('⏰ 예약 취소 완료!', 'success')
    else:
        flash('❌ 취소 실패 (이미 발행되었거나 존재하지 않음)', 'error')
    return redirect(url_for('manage_schedule'))


# ============================================
# 라우트: 글 생성 결과에서 바로 예약/발행
# ============================================
@app.route('/generate/schedule', methods=['POST'])
@login_required
def schedule_from_generate():
    """글 생성 결과에서 바로 발행예약"""
    user_id = get_user_id()
    title = request.form.get('title', '제목 없음')
    content = request.form.get('content', '')
    tags_str = request.form.get('tags', '')
    schedule_time = request.form.get('schedule_time', '')

    tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    if not schedule_time:
        flash('예약 시간을 입력해주세요.', 'error')
        return redirect(url_for('generate'))

    db.schedule_post(user_id, title, content, schedule_time, tags)
    flash(f'⏰ 발행 예약 완료! ({schedule_time})', 'success')
    return redirect(url_for('manage_schedule'))


@app.route('/generate/publish', methods=['POST'])
@login_required
def publish_now():
    """글 생성 결과에서 바로 즉시 발행"""
    user_id = get_user_id()
    title = request.form.get('title', '제목 없음')
    content = request.form.get('content', '')
    tags_str = request.form.get('tags', '')

    tags = [t.strip() for t in tags_str.split(',') if t.strip()]

    try:
        from src.posting.naver_bot import NaverBlogBot
        bot = NaverBlogBot(
            naver_id=session.get('naver_id'),
            naver_pw=session.get('naver_pw'),
            blog_id=session.get('blog_id')
        )
        success = bot.write_post(title=title, content=content, tags=tags, mode='publish')
        bot.close()

        if success:
            db.add_history(user_id, title, 'success',
                           content_preview=content[:200], source='direct')
            flash('✅ 발행 성공!', 'success')
        else:
            db.add_history(user_id, title, 'failed', source='direct')
            flash('❌ 발행 실패. 네이버 로그인 상태를 확인해주세요.', 'error')
    except Exception as e:
        flash(f'❌ 발행 오류: {str(e)}', 'error')

    return redirect(url_for('dashboard'))


# ============================================
# 라우트: 발행 이력
# ============================================
@app.route('/history')
@login_required
def history():
    user_id = get_user_id()
    history_list = db.get_history(user_id, limit=50)
    return render_template('history.html', history_list=history_list)


# ============================================
# 라우트: 이웃 관리
# ============================================
@app.route('/neighbors')
@login_required
def neighbors():
    return render_template('neighbors.html')

@app.route('/neighbors/visit', methods=['POST'])
@login_required
def visit_neighbors():
    user_id = get_user_id()
    count = int(request.form.get('count', 5))
    mode = request.form.get('mode', 'like')
    
    try:
        from src.posting.neighbor_manager import NeighborManager
        mgr = NeighborManager(
            naver_id=session.get('naver_id'),
            naver_pw=session.get('naver_pw'),
            blog_id=session.get('blog_id')
        )
        visited = mgr.visit_and_like_neighbors(count, mode=mode)
        mgr.close()
        
        action_msg = "방문 및 공감" if mode == 'like' else "방문, 공감 및 댓글 작성"
        flash(f'✅ 이웃 새글 {visited}개 {action_msg} 완료!', 'success')
    except Exception as e:
        flash(f'❌ 이웃 방문 중 오류: {str(e)}', 'error')
        
    return redirect(url_for('neighbors'))

@app.route('/neighbors/accept', methods=['POST'])
@login_required
def accept_neighbors():
    try:
        from src.posting.neighbor_manager import NeighborManager
        mgr = NeighborManager(
            naver_id=session.get('naver_id'),
            naver_pw=session.get('naver_pw'),
            blog_id=session.get('blog_id')
        )
        success = mgr.accept_neighbor_requests()
        mgr.close()
        
        if success:
            flash('✅ 서로이웃 신청 확인 완료!', 'success')
        else:
            flash('❌ 서로이웃 신청 확인 실패', 'error')
    except Exception as e:
        flash(f'❌ 오류 발생: {str(e)}', 'error')
        
    return redirect(url_for('neighbors'))


# ============================================
# 실행
# ============================================
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║  🐟 블로그 자동화 프로그램 v2.0 - 웹 대시보드            ║
║  Made by 코다리 부장 | Connect AI LAB                    ║
║                                                          ║
║  🌐 http://localhost:5000 에서 접속하세요!                ║
╚══════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
