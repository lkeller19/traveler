My website began by using the framework of finance, with the same kind of login and register function, though the css has been tweaked.

For my errors, I didn't find the bootstrap version of alerts very appealing to look at so I created my own through css and used flash
to show them when errors occured. Sometimes, I want to show a success alert, so my flash function takes in two parameters in some versions
of it, meaning the outline of my alert can appear in either red or green depending on the situation.

One change from finance is that the register page takes the user straight into the website instead of making them log in again which
I felt was reduntant whenever I had other people try out the website.

Because my website dealt with every single country in the world, I used a lot of for loops in order to cut down on the amount of hardcoded
elements of my website. For instance, when a user clicks on a country in the index page, a single html page is used to represent every single one,
depending on what is passed in to the template. I wrapped each of the cards (obtained from bootstrap) in an <a> tag and used the
url_for() function to find the function that is used to render the specific country page. With the way my for loop was set up,
I could put the country name in the address that the href went to and I could pull that address from the url and pass it into
the function which meant I knew which country to pass into the template. Also on the index page, I wanted to make them have a masonry-like
effect, so I tried to use to bootstrap card column effect. However, because of the way they loaded in vertically and there were so many of
them, it looked really spastic whenever the page loaded. Therefore, I search online to find a bricklayer class made by someone else
so I imported the script for that used that feature instead which loaded the rows horizontally.

For the navbar, I created a search box that has a <datalist> underneath it which populates with search suggestions when typing in it.
The rest of the navbar is pretty standard from finance.

Whenever I was making a page, I always tried to make sure it looked good on both large and small screens which means I utilized
media breakpoints in css in order to style things depending on screen size.

I used three different layout template pages: one for the login page, another for the upload page, and one for the rest of the site
because they were slightly different.

For the specific country pages, all of them are rendered by one single html template making use of multiple for loops to render
the comments and the images. I made the images for loop iterate in reverse so that the most recently posted images would show up first.

I have four different tables in the sql database so that I could store users, likes, comments, and the images themselves so depending on
what things are clicked and what shows up in their urls, I can pull certain things from the database which is how I can load so many
pages without having to hardcode them.

The cards with the images on them have two features which I made custom helper functions for, just like the 'usd' function from finance.
I was able to turn the timestamp associated with the comments into a 'time ago' feature and I was able to turn the timestamp of the
post date into something more readable for the user.

The comments are created in a table with a bunch of if conditions to determine what is shown. I was also able to make the table only
display up to a certain height which means that a scroll bar will then appear to view the overflow, still within that specified
maximum size.

Creating the like feature was by far the hardest part of the program because I wanted it to update on the screen without having to reload
the template. To do that, I had to use jquery and ajax which I was very unfamiliar with. Ajax was used to make a call to the backend
to one of the python functions which updated the sql database and then returned the data back to the frontend and updated the screen without refreshing.

To allow the user to upload images, I limited the file types to png, jpg, and jpeg to make sure that different filetypes wouldn't mess up the
layout. Also, I have the error alert show in a different place which is why I needed the different layout structure. I realized that
if people uploaded an image with the same name, with the way my upload structure was set up, the old picture would be overwritten and both
posts would show the same image so I imported uuid in python so that each uploaded file was given a unique name.

For the user's own posts page, I just grab from the database where the user_id equals the session user and populate the page with that
information. The user can then delete any comments on their posts or even the entire post. Deleting the entire post clears all database
reference to it, including likes and comments as well as the image file itself in the uploads folder. When the user clicks on the delete
button for either the comment or the post, a bootstrap modal first pops up on the screen just to confirm that they do in fact, want to
delete.