# Discord-Moderation-Bot — DB creation helper
# Copyright (C) 2026 Bobbythehuman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: https://github.com/bobbythehuman  (replace with email or postal address if preferred)

import sqlite3
conn = ""
cursor = ""
conn = sqlite3.connect("guild_data.db")
cursor = conn.cursor()

sql_query='''CREATE TABLE server (
	server_ID integer PRIMARY KEY,
	name string);'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE admin_role (
	serverID integer,
	role_ID integer,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE word_list (
	serverID integer,
	word string,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE letters_list (
    serverID integer,
    orig_Char string,
    replacement string,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE user_list (
	serverID integer,
	user_ID integer,
	name string,
	is_muted boolean,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE warning_list (
    serverID integer,
	userID integer,
	reason string,
	given_by string,
	date_given datetime,
    FOREIGN KEY(serverID, userID) REFERENCES user_list(serverID, user_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE notifications (
	serverID integer,
	to_Channel boolean,
	to_User boolean,
	to_Priv_Channel boolean,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE PrivChannel (
	serverID integer,
	channel_ID string,
    FOREIGN KEY(serverID) REFERENCES notifications(PrivChannels));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE separator_list (
	serverID integer,
	seperator string,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)

sql_query='''CREATE TABLE warn_operation (
	serverID integer,
	warn_count integer,
	mute_duration string,
    warn_gap string,
    FOREIGN KEY(serverID) REFERENCES server(server_ID));'''
cursor.execute(sql_query)



conn.commit()
cursor.close()
conn.close()