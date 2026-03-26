import amino
import logging
from tabulate import tabulate
from configs import menu_config
from asyncio import sleep, gather, create_task

client = amino.AsyncClient()
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger()

async def login() -> None:
    while True:
        try:
            email = input("Email: ")
            password = input("Password: ")
            await client.login(email=email, password=password)
            return
        except Exception as error:
            logger.error(error)

async def get_communities() -> int:
    while True:
        try:
            clients = await client.sub_clients(start=0, size=100)
            for index, title in enumerate(clients.name, 1):
                logger.info(f"{index}:{title}")
            community_id = clients.comId[int(input("Choose the community: ")) - 1]
            return community_id
        except Exception as error:
            logger.error(error)

async def get_chats(sub_client: amino.AsyncSubClient) -> int:
    while True:
        try:
            chats = await sub_client.get_chat_threads(size=100)
            for index, title in enumerate(chats.title, 1):
                logger.info(f"{index}:{title}")
            chat_id = chats.chatId[int(input("Choose the chat: ")) - 1]
            return chat_id
        except Exception as error:
            logger.error(error)

async def spam_messages(sub_client: amino.AsyncSubClient):
    message = input("Message to spam: ")
    target_type = input("Target type (chat/wiki/wall/blog): ")
    try:
        if target_type == "chat":
            target_id = await get_chats(sub_client)
            messaging_function = lambda: sub_client.send_message(
                chatId=target_id, message=message, messageType=0)
        else:
            link = input(f"Enter {target_type} link: ")
            target_id = (await client.get_from_code(link)).objectId
            if target_type == "wiki":
                target_id = (await client.get_from_code(link)).wikiId
                messaging_function = lambda: sub_client.comment(
                    wikiId=target_id, message=message)
            else:
                messaging_function = lambda: sub_client.comment(
                    **{f"{target_type}Id": target_id},
                    message=message)
        while True:
            await messaging_function()
            logger.info(f"Message sent to {target_type}")
    except Exception as error:
        logger.error(error)

async def retrieve_chat_id(sub_client: amino.AsyncSubClient):
    print(tabulate(menu_config.retrieve_chat_id_submenu, tablefmt=menu_config.table_style))
    choice = int(input("Choice: "))
    if choice == 1:
        public_chats = await sub_client.get_public_chat_threads(size=100)
        for title, chat_id in zip(public_chats.title, public_chats.chatId):
            print(title, chat_id)

    elif choice == 2:
        joined_chats = await sub_client.get_chat_threads(size=100)
        for title, chat_id in zip(joined_chats.title, joined_chats.chatId):
            print(title, chat_id)

async def fake_coins_transfer(sub_client: amino.AsyncSubClient):
    chat_id = await get_chats(sub_client)
    amount = int(input("Amount: "))
    await sub_client.send_coins(chatId=chat_id, coins=1)
    while True:
        await sub_client.send_coins(chatId=chat_id, coins=amount)
        logger.info("Succesfully sent coins")

async def invite_users_to_chat(sub_client: amino.AsyncSubClient):
    chat_id = await get_chats(sub_client)
    for i in range(0, 2000, 100):
        try:
            users = await sub_client.get_online_users(start=i, size=100)
            if not users.profile.userId:
                break
            invites = [sub_client.invite_to_chat(user_id, chat_id) for user_id in users.profile.userId]
            await gather([*invites])
            logger.info(f"Invited {len(users.profile.userId)} users")
            await sleep(1)
        except Exception as error:
            logger.error(error)
            continue

async def like_recent_blogs(sub_client: amino.AsyncSubClient):
    recent_blogs = (await sub_client.get_recent_blogs(start=0, size=100)).blogId
    for blog_id in recent_blogs:
        await sub_client.like_blog(blogId=blog_id)
        logger.info(f"Liked: {blog_id}")

async def follow_online_users(sub_client: amino.AsyncSubClient):
        for i in range(0, 2000, 100):
            try:
                users = await sub_client.get_online_users(start=i, size=100)
                if not users.profile.userId:
                    break
                await gather(*[
                    sub_client.follow(user_id) for user_id in users.profile.userId])
                logger.info(f"Followed {len(users.profile.userId)} users")
                await sleep(1)
            except Exception as error:
                logger.error(error)
                continue
        logger.info("Followed all online users")

async def unfollow_all_users(sub_client: amino.AsyncSubClient):
    while True:
        account_profile = await sub_client.get_user_info(
            userId=sub_client.profile.userId)
        following_count = account_profile.followingCount
        if following_count > 0:
            for i in range(0, following_count, 100):
                account_followings = await sub_client.get_user_following(
                    userId=sub_client.profile.userId, size=100)
                followings = account_followings.profile.userId
                if followings:
                    await gather(*[
                        create_task(sub_client.unfollow(user_id)) for user_id in followings])
                    logger.info("Deleting all followings")
        else:
            break

async def bulk_publish_blogs(sub_client: amino.AsyncSubClient):
    title = input("Title: ")
    content = input("Content: ")
    while True:
        await sub_client.post_blog(
            title=title, content=content, backgroundColor="#C0C0C0")
        logger.info("Published blog")

async def bulk_publish_wikis(sub_client: amino.AsyncSubClient):
    title = input("Title: ")
    content = input("Content: ")
    while True:
        await sub_client.post_wiki(
            title=title, content=content, backgroundColor="#C0C0C0")
        logger.info("Published wiki")

async def spam_system_messages(sub_client: amino.AsyncSubClient):
    chat_id = await get_chats(sub_client)
    message = input("Message: ")
    message_type = int(input("Message type: "))
    while True:
        logger.info("Spamming chat with system messages")
        await gather(*[
                create_task(sub_client.send_message(chat_id, message, message_type)) for _ in range(100)])

async def spam_chat_join_leave(sub_client: amino.AsyncSubClient):
    chat_id = await get_chats(sub_client)
    while True:
        tasks = []
        for i in range(100):
            tasks.append(create_task(sub_client.leave_chat(chatId=chat_id)))
            tasks.append(create_task(sub_client.join_chat(chatId=chat_id)))
        try:
            await gather(*tasks)
        except Exception as error:
            logger.error(error)

async def run_service():
    await login()
    community_id = await get_communities()
    sub_client = await amino.AsyncSubClient(
        comId=community_id, profile=client.profile)

    print(tabulate(menu_config.menu, tablefmt=menu_config.table_style))
    choice = int(input("Choice: "))

    if choice == 1:
        await spam_messages(sub_client)

    elif choice == 2:
        print(tabulate(
            menu_config.chat_tools, tablefmt=menu_config.table_style))
        choice = int(input("Choice: "))
        if choice == 1:
            await retrieve_chat_id(sub_client)
        elif choice == 2:
            await fake_coins_transfer(sub_client)
        elif choice == 3:
            await spam_system_messages(sub_client)
        elif choice == 4:
            await spam_chat_join_leave(sub_client)

    elif choice == 3:
        print(tabulate(menu_config.activity_tools, tablefmt=menu_config.table_style))
        choice = int(input("Choice: "))
        if choice == 1:
            await invite_users_to_chat(sub_client)
        elif choice == 2:
            await like_recent_blogs(sub_client)
        elif choice == 3:
            await follow_online_users(sub_client)
        elif choice == 4:
            await unfollow_all_users(sub_client)

    elif choice == 4:
        print(tabulate(menu_config.profile_tools, tablefmt=menu_config.table_style))
        choice = int(input("Choice: "))
        if choice == 1:
            await bulk_publish_blogs(sub_client)
        elif choice == 2:
            await bulk_publish_wikis(sub_client)

    elif choice == 5:
        exit()
