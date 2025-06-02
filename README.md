Steps to integrate Dialogflow with a backend and MySQL:

Start with Dialogflow. Create intents and write training phrases for each.

Enable webhook calls for those intents where you want your backend to receive inputs.

Create the required contexts.

Assemble the backend setup in VS Code, and run the command:

uvicorn main3:app --reload

Once you see the “Application startup complete” message in the terminal, check http://localhost:8000.

Create an HTTPS tunnel for your localhost using ngrok, and copy the generated URL.

Enter and save the ngrok URL as the Dialogflow webhook fulfillment URL.

Complete the MySQL setup. Create a database and table using the commands provided in "my_sql_table_commands".

Start a conversation in the Dialogflow chat section.

In the end, refresh and check the MySQL database for the record that was created.

