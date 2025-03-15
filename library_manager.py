import streamlit as st
import sqlite3
import pandas as pd

# Database connection function
def connect_db():
    return sqlite3.connect("library.db")

# Add a new book
def add_book(title, author, year, genre, read_status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, year, genre, read_status) VALUES (?, ?, ?, ?, ?)", 
                   (title, author, int(year), genre, int(read_status)))  # Ensure year is stored as an integer
    conn.commit()
    conn.close()

# Remove a book
def remove_book(book_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    st.success("✅ Book removed successfully!")

# Search for books
def search_books(query):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
                   (f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch all books
def fetch_books():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get statistics
def get_statistics():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books WHERE read_status=1")
    read_books = cursor.fetchone()[0]
    conn.close()
    read_percentage = (read_books / total_books) * 100 if total_books > 0 else 0
    return total_books, read_books, read_percentage

# Update a book
def update_book(book_id, title, author, year, genre, read_status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET title=?, author=?, year=?, genre=?, read_status=? WHERE id=?", 
                   (title, author, int(year), genre, int(read_status), book_id))
    conn.commit()
    conn.close()
    st.success(f"✅ Book ID {book_id} updated successfully!")

# Render styled "Read" and "Unread" labels
def render_label(status):
    if status == "Read":
        return '<span style="color: green; background-color: #e6ffe6; padding: 5px 10px; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">Read</span>'
    else:
        return '<span style="color: red; background-color: #ffe6e6; padding: 5px 10px; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">Unread</span>'

# ------- Streamlit UI --------
st.title("📚 Personal Library Manager")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["Add Book", "View Books", "Search Book", "Statistics", "Export/Import", "Edit/Delete"])

if menu == "Add Book":
    st.subheader("➕ Add a New Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    year = st.text_input("Publication Year")
    genre = st.text_input("Genre")
    read_status = st.checkbox("Have you read it?")

    if st.button("Add Book"):
        if title and author and genre and year.isdigit():
            add_book(title, author, year, genre, read_status)
            st.success(f"✅ '{title}' added to your library!")
        else:
            st.warning("⚠️ Please enter a valid year (only numbers).")

elif menu == "View Books":
    st.subheader("📚 Your Book Collection")
    books = fetch_books()
    if books:
        # Create a DataFrame for better handling
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Year", "Genre", "Read Status"])
        df["Read Status"] = df["Read Status"].apply(lambda x: "Read" if x == 1 else "Unread")

        # Apply custom styles to the "Read Status" column
        df["Read Status"] = df["Read Status"].apply(lambda x: render_label(x))
        
        # Display styled DataFrame
        st.markdown(
            df.to_html(escape=False, index=False),  # Allow HTML rendering
            unsafe_allow_html=True
        )
    else:
        st.info("📌 No books in the library yet.")

elif menu == "Search Book":
    st.subheader("🔎 Search for a Book")
    query = st.text_input("Search by title or author name")
    if st.button("Search"):
        results = search_books(query)
        if results:
            df = pd.DataFrame(results, columns=["ID", "Title", "Author", "Year", "Genre", "Read Status"])
            df["Read Status"] = df["Read Status"].apply(lambda x: "Read" if x == 1 else "Unread")

            # Apply custom styles to the "Read Status" column
            df["Read Status"] = df["Read Status"].apply(lambda x: render_label(x))
            
            # Display styled DataFrame
            st.markdown(
                df.to_html(escape=False, index=False),  # Allow HTML rendering
                unsafe_allow_html=True
            )
        else:
            st.warning("❌ No books found.")

elif menu == "Statistics":
    st.subheader("📊 Library Statistics")
    total_books, read_books, read_percentage = get_statistics()
    st.text(f"📚 Total books: {total_books}")
    st.text(f"✅ Read books: {read_books}")
    st.text(f"📈 Read percentage: {read_percentage:.2f}%")

elif menu == "Export/Import":
    st.subheader("📤 Export and 📥 Import Library")
    books = fetch_books()
    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Year", "Genre", "Read Status"])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "library.csv", "text/csv", key='download-csv')

    uploaded_file = st.file_uploader("Upload CSV to Import", type=["csv"])
    if uploaded_file:
        imported_df = pd.read_csv(uploaded_file)
        conn = connect_db()
        cursor = conn.cursor()
        for _, row in imported_df.iterrows():
            cursor.execute("INSERT INTO books (title, author, year, genre, read_status) VALUES (?, ?, ?, ?, ?)", 
                           (row["Title"], row["Author"], row["Year"], row["Genre"], row["Read Status"]))
        conn.commit()
        conn.close()
        st.success("✅ Library imported successfully!")

elif menu == "Edit/Delete":
    st.subheader("📝 Edit or Delete Books")
    books = fetch_books()
    if books:
        # Create a DataFrame for better handling
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Year", "Genre", "Read Status"])
        df["Read Status"] = df["Read Status"].apply(lambda x: "Read" if x == 1 else "Unread")
        
        # Apply custom styles to the "Read Status" column
        df["Read Status"] = df["Read Status"].apply(lambda x: render_label(x))
        
        # Display styled DataFrame
        st.markdown(
            df.to_html(escape=False, index=False),  # Allow HTML rendering
            unsafe_allow_html=True
        )

        # Input for selecting a Book ID
        book_id_input = st.text_input("Enter Book ID to Edit/Delete")
        
        if book_id_input.isdigit():
            book_id = int(book_id_input)
            
            # Check if the Book ID exists
            if book_id in df["ID"].values:
                book_row = df[df["ID"] == book_id]
                current_title = book_row["Title"].values[0]
                current_author = book_row["Author"].values[0]
                current_year = book_row["Year"].values[0]
                current_genre = book_row["Genre"].values[0]
                current_read_status = "Read" in book_row["Read Status"].values[0]
                
                # Show current details in editable fields
                st.write(f"Currently Editing Book ID: {book_id}")
                new_title = st.text_input("Title", value=current_title)
                new_author = st.text_input("Author", value=current_author)
                new_year = st.text_input("Year", value=current_year)
                new_genre = st.text_input("Genre", value=current_genre)
                new_read_status = st.checkbox("Have you read it?", value=current_read_status)
                
                # Button to Update Book
                if "update_success" not in st.session_state:
                    st.session_state.update_success = False

                if st.button("Update Book", key="update_button"):
                    if new_title and new_author and new_year.isdigit():  # Validate inputs
                        update_book(book_id, new_title, new_author, new_year, new_genre, new_read_status)
                        st.session_state.update_success = True  # Set success flag

                if st.session_state.update_success:
                        st.success(f"✅ Book ID {book_id} updated successfully!")
                        st.session_state.update_success = False  # Reset success state **after** displaying message

                # Button to Delete Book
                if st.button("Delete Book"):
                    remove_book(book_id)
                    st.success(f"✅ Book ID {book_id} deleted successfully!")
            else:
                st.warning("⚠️ Book ID not found. Please check the ID.")
        else:
            st.info("📌 Enter a numeric Book ID to proceed.")
    else:
        st.info("📌 No books in the library yet.")