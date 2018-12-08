# PriCoSha
A system for privately sharing content items among groups of people

## Dependencies 
1. Python 3.3 or higher 
2. Flask (1.0.2)
3. MySQL (Create a new database named "PriCoSha" and import [ProjTableDefs.sql](/ProjTableDefs.sql))


## Required User Cases 

- [x] **View public content**: PriCoSha shows the user the item_id, email_post, post_time,
  file_path, and item_name of public content items that were posted within the last 24
  hours. (If you prefer, you can include this with use case (3) below).
- [x] **Login**: The user enters e-mail and password. PriCoSha checks whether the hash of the
  password matches the stored password for that e-mail. If so, it initiates a session, storing
  the e-mail and any other relevant data in session variables, then goes to the home page
  (or provides some mechanism for the user to select their next action.) If the password
  does not match the stored password for that e-mail (or no such user exists) PriCoSha
  informs the user that the the login failed and does not initiate the session.
- [x] **View shared content items and info about them**: PriCoSha shows the user the
  item_id, email_post, post_time, file_path, and item_name of content items that are
  visible to the her, arranged in reverse chronological order. (Optionally, include a link to
  an actual content item or a way to display it.)
  Along with each content item there should be a way for the user to see further
  information, including
  a. first name and last name of people who have been tagged in the content item
  (taggees), provided that they have accepted the tags (Tag.status == true)
  b. Ratings of the content item 
- [x] **Manage tags**: PriCoSha shows the user relevant data about content items that have
  proposed tags of this user (i.e. user is the taggee and status false.) User can choose to
  accept a tag (change status to true), decline a tag (remove the tag from Tag table), or
  not make a decision (leave the proposed tag in the table with status == false.)
- [x] **Post a content item**: User enters the relevant data (and optionally, a link to a real
  content item) and a designation of whether the content item is public or private.
  PriCoSha inserts data about the content item (including current time, and current user as
  owner) into the Content table. If the content item is private, PriCoSha gives the user a
  way to designate FriendGroups that the user belongs to with which the Photo is shared.
- [x] **Tag a content item**: Current user, who we’ll call x, selects a content item that is visible
  to her and proposes to tag it with e-mail y
  a. If the user is self-tagging (y == x), PriCoSha adds a row to the Tag table:
  (item_id, x, x, TIMESTAMP, true)
  b. else if the content item is visible to y, PriCoSha adds a row to the Tag table:
  (ID, x, x, TIMESTAMP, false)
  c. else if content item is not visible to y, PriCoSha doesn’t change the tag table and
  prints some message saying that it cannot propose this tag.
- [x] **Add friend**: User selects an existing FriendGroup that they own and provides first_name
  and last_name. PriCoSha checks whether there is exactly one person with that name
  and updates the Belong table to indicate that the selected person is now in the
  FriendGroup. Unusual situation such as multiple people with the same name and the
  selected person already being in the FriendGroup should be handled gracefully

## Optional User Cases

- [x] **Quit Group**: Users can scroll down groups that they join and select a friend group to quit. If anyone trys to quit a friend group he/she owns, it would fail and an error message would display. 
- [x] **Add comments**: Users can comment emojis about content that is visible to them. :heart_eyes: Information of who commented the content item and the comment time can be found besides each content item. 
- [x] **Defriend**: Owners of friends groups are able to defriend other users. Once the defriend is successful, tags of the defriended user won't get display anymore but comments will. 
- [x] **Tagging a group**: Include an
  additional tagging mechanism, where multiple people in a content item can be tagged
  together, but which will only be visible if all of them agree to make it visible.
  
## Team Contribution
* **Bixing Xie** - (https://github.com/bixingxie)
  * Initial setup of Flask, mySQL, and github
  * User case: Register
  * User case: Login 
  * User case: Tag a content item (single user) 
  * User case: Add comments 
  * User case: Quit group
* **Chen Zhou** - (https://github.com/ChenZ0912)
  * User case: View public content
  * User case: View shared content items and info about them
  * User case: Post a content item
  * User case: Add friend
  * User case: Tagging a group
* **Ninglu Ma** - (https://github.com/bannim)
  * User case: View public content
  * User case: View shared content items and info about them
  * User case: Post a content item
  * User case: Tag a content item (single user) 
  * User case: Tagging a group
  * User case: Defriend
