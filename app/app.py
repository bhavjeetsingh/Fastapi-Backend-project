from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import os
import uuid
import shutil
import tempfile
from app.users import auth_backend, current_active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
app = FastAPI(lifespan=lifespan)
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=['auth'])
app.include_router(fastapi_users.get_auth_router(UserRead, UserCreate), prefix='/auth', tags=['auth'])
app.include_router(fastapi_users.get_auth_router(), prefix='/auth', tags=['auth'])
app.include_router(fastapi_users.get_auth_router(UserRead), prefix='/auth', tags=['auth'])
app.include_router(fastapi_users.get_auth_router(UserRead, UserUpdate), prefix='/users', tags=['users'])

# creating posts and saving to database
@app.post('/upload', response_model=PostResponse)
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(''),
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file,temp_file)
        with open(temp_file_path, 'rb') as upload_stream:
            upload_result = imagekit.files.upload(
                file=upload_stream,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=['backend-upload']
            )

        post = Post(
            caption=caption,
            url=upload_result.url,
            file_type='video' if (file.content_type or '').startswith('video/') else 'image',
            file_name=upload_result.name
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        file.file.close()
@app.get('/feed') # retrieving from database
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    posts_data = []
    for post in posts:
        posts_data.append(
            {'id': str(post.id),
             'caption': post.caption,
             'url': post.url,
             'file_type': post.file_type,
             'file_name': post.file_name,
             'created_at': post.created_at.isoformat()}
        )

    return {'posts': posts_data}

@app.delete('.posts/{post_id}')
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.excute(select(Post).where(Post.id == post_uuid))
        post = result.sclars().first()
        if not post:
            raise HTTPException(status_code=404,detail='Postnot found') 
        
        await session.delete(post)
        await session.commit()
        return{'success': True, "message": 'Post deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, details=str(e))