#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import pymysql.cursors
import json


def fetch_group_list(cursor):
    query_select_group = """
                        SELECT *
                        FROM FriendGroup
                        WHERE owner_email = %s
                """
    cursor.execute(query_select_group, (session['email']))
    groups = cursor.fetchall()
    return groups



#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='',
                       db='PriCoSha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
#
#Define a route to hello function
@app.route('/')
def hello():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE email = %s and password = SHA2(%s, 256)'
    cursor.execute(query, (email, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None

    if(data):
        #creates a session for the the user
        #session is a built in
        session['email'] = email
        session['fname'] = data['fname']
        session['lname'] = data['lname']
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or email'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None

    if(data):
        #If the previous query returns data, then user exists
        error = "This person already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, SHA2(%s, 256), %s, %s)'
        cursor.execute(ins, (email, password, fname, lname))
        conn.commit()
        cursor.close()
        return render_template('login.html')


@app.route('/home', methods=['POST', "GET"])
def home():
    person = session['email']
    fname = session['fname']
    lname = session['lname']
    # cursor = conn.cursor()
    # query = '''SELECT *
    #                             FROM ContentItem
    #                             WHERE (is_pub = 1 OR
    #                                 item_id IN (
    #                                         SELECT item_id
    #                                         FROM Belong NATURAL JOIN Share
    #                                         WHERE email = %s
    #                                 )
    #                             )
    #                             AND post_time > TIMESTAMPADD(DAY, -1, CURRENT_TIMESTAMP())
    #                             ORDER BY post_time DESC'''
    # cursor.execute(query, (person))
    #
    # data = cursor.fetchall()
    # query = """
    #                             SELECT *
    #                             FROM Friendgroup
    #                             WHERE owner_email = %s
    #                     """
    # cursor.execute(query, (person))
    # group_data = cursor.fetchall()

    return render_template('home.html', person=person, fname = fname, lname = lname)

@app.route('/getPage', methods=['GET', 'POST'])
def getPage():
    cursor = conn.cursor()
    # PC: Public Content
    person = session['email']
    if request.form['page'] == 'browseContent':
        query = '''SELECT * 
                            FROM ContentItem
                            WHERE (
                                (is_pub = 1) OR 
                                item_id IN (
                                        SELECT item_id
                                        FROM Belong NATURAL JOIN Share
                                        WHERE email = %s
                                )
                            )    
                            AND post_time > TIMESTAMPADD(DAY, -1, CURRENT_TIMESTAMP())
                            ORDER BY post_time DESC'''
        cursor.execute(query, (person))

        data = cursor.fetchall()
        query = """
                            SELECT *
                            FROM Friendgroup
                            WHERE owner_email = %s
                    """
        cursor.execute(query, (person))
        group_data = cursor.fetchall()
        cursor.close()
        return render_template('features/browseContent.html', posts=data, groups=group_data)

    elif request.form['page'] =='post_t':
        query = 'SELECT * FROM ContentItem WHERE email_post = %s ORDER BY post_time DESC'
        cursor.execute(query, (person))
        data = cursor.fetchall()

        query = """
            SELECT *
            FROM Friendgroup
            WHERE owner_email = %s
            """
        cursor.execute(query, (person))
        group_data = cursor.fetchall()
        cursor.close()
        return render_template('features/post.html', groups=group_data, posts = data)

    elif request.form['page'] == 'createGroup':
        query = """
                    SELECT *
                    FROM Friendgroup
                    WHERE owner_email = %s
            """
        cursor.execute(query, (person))
        group_data = cursor.fetchall()

        query = '''
                SELECT owner_email, fg_name
                FROM Belong
                WHERE email = %s
            '''
        cursor.execute(query, (person))
        joined_groups = cursor.fetchall()
        cursor.close()
        return render_template('features/createGroup.html', groups=group_data, joined_groups=joined_groups)

    elif request.form['page'] == 'tag':
        query = '''
                SELECT item_id, tagtime, email_tagger, email_post, post_time, item_name, status
                FROM Tag NATURAL JOIN ContentItem
                WHERE email_tagged = %s AND (status != 'ind-accepted' AND status != 'group-accepted') 
            '''

        cursor.execute(query, (person))
        tags = cursor.fetchall()
        cursor.close()
        return render_template('features/tag.html', tags=tags)
    elif request.form['page'] == 'quitGroup':
        query = """
                    SELECT *
                    FROM Belong
                    WHERE email = %s
                    """
        cursor.execute(query, (person))
        group_data = cursor.fetchall()
        cursor.close()
        return render_template('features/quitGroup.html', groups=group_data)
    else:
        return render_template('features/' + request.form['page'] + '.html')

@app.route('/post', methods=['GET', 'POST'])
def post():
    email = session['email']
    item_name = request.form['item_name']
    file_path = request.form['file_path']
    is_pub = request.form['is_pub']
    cursor = conn.cursor()
    query = '''
               INSERT INTO ContentItem (email_post, post_time, file_path, item_name, is_pub) 
               VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s)
            '''
    try:
        cursor.execute(query, (email, file_path, item_name, is_pub))

    except:
        conn.rollback()

    query_getID = '''
                SELECT item_id
                FROM ContentItem
                WHERE email_post = %s AND file_path = %s AND item_name = %s AND is_pub = %s
                AND post_time = (
                    SELECT MAX(post_time)
                    FROM ContentItem
                    WHERE email_post = %s AND file_path = %s AND item_name = %s AND is_pub = %s
                )
            '''
    cursor.execute(query_getID, (email, file_path, item_name, is_pub, email, file_path, item_name, is_pub))
    itID = cursor.fetchone()



    if is_pub == '0':
        fg = request.form['fgSharedWith']
        ins = '''
           INSERT INTO Share (owner_email, fg_name, item_id) VALUES (%s, %s, %s)
           '''

        cursor.execute(ins, (email, fg, itID['item_id']))
    conn.commit()


    query = 'SELECT * FROM ContentItem WHERE email_post = %s ORDER BY post_time DESC'
    cursor.execute(query, (session['email']))
    data = cursor.fetchall()

    cursor.close()

    return jsonify(message='Successful!',
        data = render_template('features/contentTable.html', posts = data)
    )


#If form createGroup in "home.html" is submitted, this function will be called
@app.route('/createGroup', methods = ['GET', 'POST'])
def createGroup():
    email = session['email']
    fg_name = request.form['fg_name']
    description = request.form['description']
    cursor = conn.cursor()
    query_select_group = """
            SELECT *
            FROM FriendGroup
            WHERE owner_email = %s AND fg_name = %s
    """
    cursor.execute(query_select_group, (email, fg_name))
    data = cursor.fetchall()
    # Check whether this group has been created, and pass the message back to home()
    if data:
        cursor.close()
        return jsonify({
            'message': fg_name + " has already been created. Please use a different group name",
            'data': render_template('features/group_template.html', groups=data)
        })
    else:
        # Insert the group into FriendGroup
        query = """
                INSERT INTO FriendGroup (owner_email, fg_name, description)
                VALUES (%s, %s, %s)
        """
        cursor.execute(query, (email, fg_name, description))
        conn.commit()
        # Add the owner to the Belong
        query = """
            INSERT INTO Belong (email, owner_email, fg_name) VALUES (%s, %s, %s)
        """
        cursor.execute(query, (email, email, fg_name))
        conn.commit()

        groups=fetch_group_list(cursor)

        query = '''
                    SELECT owner_email, fg_name
                    FROM Belong
                    WHERE email = %s
            '''
        cursor.execute(query, (session['email']))
        joined_groups = cursor.fetchall()
        cursor.close()
        return jsonify({
            'message':"Successfully created group {}!".format(fg_name),
            'my-group':render_template('features/group_template.html', groups=groups),
            'joined-group':render_template('features/joinedGroup_template.html', joined_groups=joined_groups)
        })
        # return render_template('features/createGroup.html', message = "Successfully created group {}!".format(fg_name))


@app.route('/searchUsr', methods = ['GET', 'POST'])
def searchUsr():
    toSearch_fname = request.form['fname']
    toSearch_lname = request.form['lname']
    search_for = request.form['search_for']
    file_name = 'searchUsr_toAdd.html'
    if search_for == "Delete":
        file_name = 'searchUsr_toDelete.html'
    cursor = conn.cursor()
    query = """
        SELECT email
        FROM Person
        WHERE fname = %s AND lname = %s
    """
    cursor.execute(query, (toSearch_fname, toSearch_lname))
    data = cursor.fetchall()

    query_select_group = """
                    SELECT *
                    FROM FriendGroup
                    WHERE owner_email = %s
            """
    cursor.execute(query_select_group, (session['email']))
    groups = cursor.fetchall()

    cursor.close()

    if not groups:
        return render_template('features/' + file_name, message="You have no group!")
    if data:
        if search_for == "Add":
            return render_template('features/addFriends.html', candidate_usrs = data, groups=groups)
        elif search_for == "Delete":
            return render_template('features/deleteFriend.html', candidate_usrs = data)
    else:
        return render_template('features/' + file_name, message =
        "Cannot find {} {}, please confirm the name of the person you are adding".format(toSearch_fname, toSearch_lname))

@app.route('/addFriend', methods = ['GET', 'POST'])
def addFriend():
    if request.form['submit_button'] == "Cancel":
        return render_template("features/searchUsr_toAdd.html")

    elif request.form['submit_button'] == "Add":
        owner_email = session['email']
        fg_name = request.form['fg_name']
        toAdd_email = request.form['usr']
        cursor = conn.cursor()

        query = """
                SELECT *
                FROM belong 
                WHERE email = %s AND owner_email = %s AND fg_name = %s
        """

        cursor.execute(query, (toAdd_email, owner_email, fg_name))
        exists = cursor.fetchone()
        if exists:
            cursor.close()
            return jsonify(message="{} already exists in friend group {}".format(toAdd_email, fg_name))
        else:
            query = """
                  INSERT INTO Belong (email, owner_email, fg_name) VALUES (%s, %s, %s)
            """
            cursor.execute(query, (toAdd_email, owner_email, fg_name))
            conn.commit()
            cursor.close()
            return jsonify(message="{} successfully added to friend group {}".format(toAdd_email, fg_name))


    # query = """
    #     SELECT *
    #     FROM Belong
    #     WHERE owner_email = %s AND email = %s AND fg_name = %s
    # """
    # cursor.execute(query, (owner_email, email, fg_name))
    # data = cursor.fetchall()
    # if not data:
    #     query = """
    #         INSERT INTO Belong (email, owner_email, fg_name) VALUES (%s, %s, %s)
    #     """
    #     cursor.execute(query, (email, owner_email, fg_name))
    #     conn.commit()

# @app.route('/select_blogger')
# def select_blogger():
#     #check that user is logged in
#     #username = session['username']
#     #should throw exception if username not found
#
#     cursor = conn.cursor();
#     query = 'SELECT DISTINCT email FROM ContentItem'
#     cursor.execute(query)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('select_blogger.html', user_list=data)
#
# @app.route('/show_posts', methods=["GET", "POST"])
    
#def show_posts():
#    poster = request.args['poster']
#    cursor = conn.cursor();
#    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#    cursor.execute(query, poster)
#    data = cursor.fetchall()
#    cursor.close()
#    return render_template('show_posts.html', poster_name=poster, posts=data)
    
@app.route('/browse')
def browse():
    try:
        message = request.args["message"]
    except:
        message = ""

    cursor = conn.cursor()
    query = '''SELECT * 
                    FROM ContentItem
                    WHERE (is_pub = 1 OR 
                        item_id IN (
                                SELECT item_id
                                FROM Belong NATURAL JOIN Share
                                WHERE email = %s
                        )
                    )
                    AND post_time > TIMESTAMPADD(DAY, -1, CURRENT_TIMESTAMP())
                    ORDER BY post_time DESC'''
    cursor.execute(query, (session['email']))
    data = cursor.fetchall()
    cursor.close()
    return redirect(url_for('home', posts = data, message = message))

@app.route('/tag', methods = ["POST", "GET"])
def tag():
    tagger_email = session['email']
    item_id = request.form['item_id']
    cursor = conn.cursor()
    # 如果是tag一个人
    if request.form['tag_choice'] == "tag-single":
        tagged_email = request.form['taggedEmail']

        query = '''
               SELECT * FROM Person WHERE email = %s
               '''
        cursor.execute(query, (tagged_email))
        data = cursor.fetchone()
        # edge case: tagged_email not registered
        if not data:
            return jsonify(message=
            "Tagging failed, {} is not a valid registered user".format(tagged_email))

        query = '''
               SELECT item_id
               FROM ContentItem
               WHERE is_pub = 1
               UNION
               SELECT item_id
               FROM Share NATURAL JOIN Belong
               WHERE email = %s AND item_id = %s
               '''
        cursor.execute(query, (tagged_email, item_id))
        data = cursor.fetchall()
        # edge case: tagged_email doesn't have access to the post
        if not data:
            return jsonify(message=
            "Tagging failed, {} has no access to post {}".format(tagged_email, item_id))
        else:
            # egde case: user already tagged
            query = '''
                   SELECT *
                   FROM Tag
                   WHERE email_tagged = %s AND email_tagger = %s AND item_id = %s
                   '''
            cursor.execute(query, (tagged_email, tagger_email, item_id))
            data = cursor.fetchone()

            if data:
                if data['status'] == 'group-pending':
                    query = '''UPDATE Tag
                                SET status = 'ind-pending'
                                WHERE email_tagged = %s AND email_tagger = %s AND item_id = %s
                    '''
                    cursor.execute(query, (tagged_email, tagger_email, item_id))
                elif data['status'] =='group-accepted':
                    query = '''UPDATE Tag
                                SET status = 'ind-accepted'
                                WHERE email_tagged = %s AND email_tagger = %s AND item_id = %s
                            '''
                    cursor.execute(query, (tagged_email, tagger_email, item_id))
                conn.commit()
                cursor.close()
                return jsonify(message=
                               "tag request successfully sent to {}".format(tagged_email))
            else:
                    query = '''
                    INSERT INTO Tag(email_tagged, email_tagger, item_id, status, tagtime)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP())
                    '''
                    # checks if self-tagging
                    if tagged_email == tagger_email:
                        cursor.execute(query, (tagged_email, tagger_email, item_id, 'ind-accepted'))
                    else:
                        cursor.execute(query, (tagged_email, tagger_email, item_id, 'ind-pending'))
                    conn.commit()
                    cursor.close()
                    return jsonify(message=
                                   "tag request successfully sent to {}".format(tagged_email))



    elif request.form['tag_choice'] == "tag-group":
        # 网页上需有一个下拉菜单显示此user的所有fg_name
        toTag_fg = request.form['toTag_fg']

        # pick all members in this friend group who have not accepted the tagging request by this user under this post before
        cursor = conn.cursor()


        query ='''
            SELECT *
            FROM Share
            WHERE owner_email = %s AND fg_name = %s AND item_id = %s
        '''

        cursor.execute(query, (session['email'], toTag_fg, item_id))
        data = cursor.fetchall()

        query='''
            SELECT *
            FROM ContentItem
            WHERE item_id = %s AND is_pub = 1
        '''
        cursor.execute(query, item_id)

        is_public = cursor.fetchall()
        if not data and not is_public:
            return jsonify(message="You didn't share this post with this group!")
        query = """
                       SELECT email
                       FROM Belong
                       WHERE owner_email = %s AND fg_name = %s AND email not in
                       (SELECT email_tagged
                       FROM Tag
                       WHERE item_id = %s and email_tagger = %s)
                       """

        cursor.execute(query, (tagger_email, toTag_fg, item_id, tagger_email))
        conn.commit()

        email_list = cursor.fetchall()  # 需要把email_list send to html,然后在 managetag 里可以知道这一个group里有哪些成员。


        # either this group is empty or this group has been tagged
        if len(email_list) == 0:
            return jsonify(message="Tagging failed, all members in \"{}\" have already been tagged to post {}".format(
                                         toTag_fg, item_id))
        else:
        # delete the records "those in this FG who have received individual tag as but status is pending
        #            query = '''
        #            DELETE FROM Tag
        #            WHERE email_tagger = %s AND item_id = %s AND is_group_tagged = False and status = '0' and email_tagged in
        #            (SELECT email
        #            FROM Belong
        #            WHERE owner_email = %s AND fg_name = %s)
        #            '''
        #            cursor.execute(query, (tagger_email, item_id, tagger_email, toTag_fg))
        #            conn.commit()
        #                             ##            those_already_receive_indi_tag_but_is_pending = cursor.fetchall()

            query = '''
                           INSERT INTO `Tag`(`email_tagged`, `email_tagger`, `item_id`, `status`, `tagtime`)
                           VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP())
                           '''

            for email in email_list:
                if tagger_email == email['email']:
                    cursor.execute(query, (email['email'], tagger_email, item_id, 'group-accepted'))
                else:
                    cursor.execute(query, (email['email'], tagger_email, item_id, 'group-pending'))
            conn.commit()
            cursor.close()
            return jsonify(message="tag request successfully sent to \"{}\" ".format(toTag_fg))


@app.route('/ManageTag', methods=['GET', 'POST'])
def ManageTag():
    #    email_tagged = request.form['email_tagged']
    email_tagged = session['email']
    email_tagger = request.form['email_tagger']
    item_id = request.form['item_id']
    # status 是被tagged的人接受 1 或者不接受 0
    status = request.form['status']

    # item_status 是数据库中这个item的status的值 (group-pending 或者 individual-pending)
    item_status = request.form['item_status']
    cursor = conn.cursor()

    updated_status = "ind-accepted"
    if "group" in item_status:
        updated_status = "group-accepted"

    if status == '1':  # accept the request, update Dadabase status to True. 需要更新 home
        query = """
            UPDATE Tag
            SET status = %s
            WHERE email_tagged = %s and email_tagger = %s and item_id = %s"""

        cursor.execute(query, (updated_status, email_tagged, email_tagger, item_id))
        conn.commit()


    elif status == '0':  # reject the request, delete tag from Tag table
        query = "DELETE FROM Tag WHERE email_tagged = %s and email_tagger = %s and item_id = %s"
        cursor.execute(query, (email_tagged, email_tagger, item_id))
        conn.commit()

    cursor.close()
    return jsonify(message="Successful!")

@app.route('/rate', methods = ["POST", "GET"])
def rate():
    if request.form['submit_button'] == "Rate":
        email = session['email']
        item_id = request.form['item_id']
        emoji = request.form['emoji']
        cursor = conn.cursor()

        query = """
            SELECT * FROM Rate WHERE email = %s AND item_id = %s
        """
        cursor.execute(query, (email, item_id))
        data = cursor.fetchone()
        if data:
            query = """
            UPDATE `Rate` SET `rate_time` = CURRENT_TIMESTAMP(),`emoji`= %s WHERE 
            `email` = %s AND `item_id` = %s
            """
            cursor.execute(query, (emoji, email, item_id))
            conn.commit()
            cursor.close()
            return jsonify(message="Rating successfully modified!")
        else:
            query = """
            INSERT INTO `Rate`(`email`, `item_id`, `rate_time`, `emoji`) 
            VALUES (%s, %s, CURRENT_TIMESTAMP(), %s)
            """
            cursor.execute(query, (email, item_id, emoji))
            conn.commit()
            cursor.close()
            return jsonify( message="Successfully rated!")


@app.route('/getFG', methods=['GET', 'POST'])
def getUsrFG():
    owner_email = session['email']
    toDelete_email = request.form['toDelete_usr']
    cursor = conn.cursor()
    if toDelete_email == owner_email:
        cursor.close()
        return jsonify(
            message="Deleting failed. Cannot delete yourself."
        )
    query = """
                SELECT fg_name
                FROM belong 
                WHERE email = %s AND owner_email = %s
        """
    cursor.execute(query, (toDelete_email, owner_email))
    fg_names = cursor.fetchall()
    cursor.close()
    if not fg_names:
        return jsonify(
            message="{} is not your friend.".format(toDelete_email)
        )
        # return redirect(url_for('home', deFriend_message=
        # "{} is not your friend.".format(toDelete_email)))

    else:
        return jsonify(
            data=render_template('features/listGroup.html', groups=fg_names)
        )


@app.route('/deFriend', methods=['GET', 'POST'])
def deleteFriend():
    if request.form['submit_button'] == "Cancel":
        return render_template('features/searchUsr_toDelete.html')

    elif request.form['submit_button'] == "Delete":
        fg_name = request.form['fg_name']
        owner_email = session['email']
        toDelete_email = request.form['toDelete_email']  # 我要怎么得到你！

        cursor = conn.cursor()

        query = '''
            DELETE FROM Belong 
            WHERE email = %s AND owner_email = %s AND fg_name = %s
        '''
        # (email, owner_email, fg_name)
        # VALUES( % s, % s, % s)
        cursor.execute(query, (toDelete_email, owner_email, fg_name))
        conn.commit()
        cursor.close()

        return jsonify(message=
        "{} successfully deleted from your friend group {}".format(toDelete_email, fg_name))


@app.route('/contentDetail', methods=['POST', 'GET'])
def contentDetail():
    item_id = request.form['item_id']
    cursor = conn.cursor()
    # 一个收集所有要显示的usr的set
    usr_toShow = set()

    # individual tag 的情况
    query = '''
        SELECT email_tagged, email_tagger, tagtime
        FROM Tag
        WHERE item_id = %s AND status = "ind-accepted"
        '''
    cursor.execute(query, (item_id,))
    ind_tag_info = cursor.fetchall();
    for info in ind_tag_info:
        email_tagger=info['email_tagger']
        email_tagged=info['email_tagged']
        tagtime=info['tagtime']
        usr_toShow.add((email_tagger, email_tagged, tagtime))

    # group-tag的情况
    # 先找所有tagger以及他tag的组
    query = '''
        SELECT Tag.email_tagger,  Belong.fg_name
        FROM Belong JOIN Tag ON (Tag.email_tagger = Belong.owner_email AND Tag.email_tagged = Belong.email)
        WHERE Tag.item_id = %s
        GROUP BY  Tag.email_tagger, Belong.fg_name
        '''

    cursor.execute(query, (item_id,))
    group_info = cursor.fetchall();

    # 这个query找出每个组中接受的人的数量
    query_num_accepted = '''
        SELECT COUNT(*) AS num_accepted
        FROM Belong RIGHT JOIN Tag ON (Tag.email_tagger = Belong.owner_email AND Tag.email_tagged = Belong.email)
        WHERE item_id = %s AND fg_name = %s AND email_tagger = %s AND (status = 'ind-accepted' OR status='group-accepted') 
         '''
    # 这个query找出每个组中的人的数量
    query_num = '''
        SELECT COUNT(*) AS num
        FROM Belong RIGHT JOIN Tag ON (Tag.email_tagger = Belong.owner_email AND Tag.email_tagged = Belong.email)
        WHERE fg_name = %s AND email_tagger = %s
        '''
    # 这个query找出这个组中所有成员的信息
    query_memeber = '''
        SELECT Tag.email_tagged, Tag.email_tagger, Tag.tagtime
        FROM Belong RIGHT JOIN Tag ON (Tag.email_tagger = Belong.owner_email AND Tag.email_tagged = Belong.email)
        WHERE Belong.fg_name = %s AND Belong.owner_email = %s
        '''
    # 存放所有要显示的组
    groups_toShow = []
    # 检查每一个被tagged的组
    for group in group_info:
        fg_name = group['fg_name']
        email_tagger = group['email_tagger']

        cursor.execute(query_num_accepted, (item_id, fg_name, email_tagger))
        num_accepted = cursor.fetchone()['num_accepted']

        cursor.execute(query_num, (fg_name, email_tagger))
        num = cursor.fetchone()['num']
        # 如果这个组中所有人都接受，加入到list中
        if num_accepted == num:
            groups_toShow.append(group)

    # 从要显示的组中找出所有tagger，tagged，tagtime
    for group in groups_toShow:
        cursor.execute(query_memeber, (group['fg_name'], group['email_tagger']))
        for info in cursor.fetchall():
            email_tagger = info['email_tagger']
            email_tagged = info['email_tagged']
            tagtime = info['tagtime']
            usr_toShow.add((email_tagger, email_tagged, tagtime))

    # 找出rate的信息相关
    query = '''
        SELECT email, rate_time, emoji
        FROM Rate
        WHERE item_id = %s
        '''

    cursor.execute(query, (item_id))
    rate_info = cursor.fetchall()

    cursor.close()
    return render_template('features/contentDetail.html', tag_info=usr_toShow, rate_info=rate_info)

@app.route('/quitGroup', methods = ["POST"])
def quitGroup():
    if request.form["submit_button"] == "Quit":
        email = session['email']
        info = json.loads(request.form['info'])

        owner_email = info['owner_email']
        fg_name = info['fg_name']
        if email == owner_email:
            return jsonify(message = "You cannot quit a group that you own!")

        query = """
            DELETE FROM Belong 
            WHERE email = %s AND owner_email = %s AND fg_name = %s
        """
        cursor = conn.cursor()
        cursor.execute(query, (email, owner_email, fg_name))
        conn.commit()
        cursor.close()
        return jsonify(message = "Successfully quit group {}".format(fg_name))


@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')
#
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
