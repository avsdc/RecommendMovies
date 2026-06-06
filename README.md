# Movie Recommender

## Description:

MoviesRecommender uses Python and Flask. 
When the app is run from the anaconda prompt, the app runs on localhost and port 5000. The index.html file is
displayed with two forms for two methods of filtering i.e. content and collaborative. The form is blank
at first, but two lists movies and users are sent to index.html by render_template method.There are also two 
functions for recommending movies. The first function get_content_filtered_recommendations(movie_title, top_n)
takes as parameters a movie_title, and top_n. The movie_title is selected from a datalist dropdown box that 
appears on the user interface in the form with "name" filter_type and value "content".
The <datalist> element in HTML allows an autocomplete feature that provides a predefined list of suggestions for
an <input> field. The user can select a value from list, or even enter a custom value. After entering the 
movie_title, and when the button next to it is clicked, the form index.html continues to be displayed, as method
is "POST", and action for form is specified as "/" endpoint, so index function gets executed. 
The 'filter_type' "name" of input type of first form is retrieved from the form in index function through the
'request.form.get' method, and 'movie_title' that is selected is passed within the index function through 
'request.form.get' method as 'target1'. In turn, 'target1' is passed to the get_content_filtered_recommendations.
Content filtering recommends movies based on the inherent characteristics of the content, movies similar to
the movie_title selected are recommended.
Likewise, the second form's filter_type has a value of collaborative. When a user is selected on the datalist dropdown
box for this form, and button next to it is clicked, method is again "POST", and index function gets executed. The filter_type
now is "collaborative", and in the else statement 'request.form.get' retrieves the user as 'target2' that is passed to the
get_collaborative_rcommendations function, and recommendations are displayed at the bottom of the form.Collaborative
filtering predicts user preference by determining patterns between similar users.
In the index function three session variables val1, val2, refs are created for target1, target2, and recommendations.
Due to using session variables, the movie_title selected in the first form continues to be selected, even after the 
button is clicked.
Similarly, userId continues to be selected, even after the second button is clicked. These session variables are
passed to the render_template method.

## Attribution:
Image displayed on user interface:
<a href="http://www.freepik.com">Designed by gstudioimagen / Freepik</a>

