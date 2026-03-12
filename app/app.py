from fastapi import FastAPI, HTTPException
from app.schemas import PostCreate, PostResponse
app = FastAPI()
text_posts = {
    1: {'title': 'new post', 'content': 'cool test post'},
    2: {'title': 'second post', 'content': 'this is the second post'},
    3: {'title': 'third post', 'content': 'another interesting post'},
    4: {'title': 'fourth post', 'content': 'some more content here'},
    5: {'title': 'fifth post', 'content': 'halfway through the posts'},
    6: {'title': 'sixth post', 'content': 'keeping the content flowing'},
    7: {'title': 'seventh post', 'content': 'almost there with the posts'},
    8: {'title': 'eighth post', 'content': 'great content in this post'},
    9: {'title': 'ninth post', 'content': 'nearing the end of the list'},
    10: {'title': 'tenth post', 'content': 'final post in the collection'},
}
@app.get('/posts/')
def get_all_posts(limit:int):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts


@app.get('/posts/{id}')
def get_post(id: int)-> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail='Post not found')
    return text_posts.get(id)

@app.post('/posts')
def create_post(post: PostCreate)-> PostResponse:
    new_post = {'title': post.title, 'content': post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post    

 