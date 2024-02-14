# Pass Office Management System

https://github.com/yongdetan/passoffice_management_system/assets/61530179/620eec9b-41fc-4117-8df0-4731d9a9c68d

# Overview

Pass Office Management System (POMS) is a web application that allows users (commanders) to manage their troopers' offs and leaves and enable them to better plan and analyse troopers' hours through a dashboard. 

POMS was developed with Django framework. PostgreSQL was the chosen database to store data that will be produced by the users. In order to create the charts that are in the dashboard, ChartJS is used as it provides the right amount of flexbility needed to customize the charts.

Python Virtual Environment is also used to organize all the libraries that are required for the web application and it is using the same version.

# Motivation

This web application was created when I was serving my national service. There are two main reasons why I created this web application.

- Firstly, there was a period where the superiors wanted to track each and every trooper's offs. Since offs are 'privileges' given by superiors, it is much more difficult to track them compared to leaves whereby the trooper can just access the NS portal to view them.
  
  The previous methods of tracking offs used by the sergeants were either through excel or their personal note app. However, there will be always be arguments between the commanders and the troopers with this system as human error will definitely occur. As such, to ensure accuracy and prevent human error from occuring, the offs and leaves feature was developed in this web application.

  To kill two birds with one stone, I discussed with my commander and decided to include duty planning within the application and integrate a dashboard with charts displaying the hours and duty completed by the troopers. Prior to this, my commander was using excel sheet to plan the duty. While there is nothing wrong with using an excel sheet, it is difficult for him to track each and every individual's hours and the type of duty they have done every week as more and more excel sheets are generated daily. Thus, with the dashboard and duty scheduling feature, it also allows the commanders to better plan their troopers' duty fairly.
  
- Secondly, I wanted to learn more about web development and and brush up my problem solving and database skills. As my ORD date gets nearer, I realize that it was time for me to get back into reality and start preparing for university and the workforce. The reason why I chose to develop POMS in Python with Django instead of using another language which I have used before like C# is because I found that most data engineering jobs require me to use either Python, Java or Scala. Since my current goal is still to become a data engineer in the future, I chose to stick with Python and deepen my knowledge in it.
