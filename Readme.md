# Urban Shopper - Grocery App

## Overview

Urban Shopper is a comprehensive grocery app, drawing inspiration from popular platforms like Blinkit and Swiggy. This project focuses on creating a seamless user experience, incorporating features such as Role-Based Access Control (RBAC) for admin and manager logins. Users can engage in activities like browsing products, adding items to their carts, and completing the checkout process. The application also includes functionalities like daily reminders and monthly analysis reports to enhance user engagement.

## Tech Stack

### Backend
- **Flask**
  - Utilizes Flask Sqlalchemy for efficient ORM (Object-Relational Mapping) for modals like user and products.
  - Implements Flask JWT Extended for secure authentication token generation.
  - Employs Flask CORS to facilitate cross-origin resource sharing.

### Frontend
- **Vue.js**
  - Developed using Vue CLI for streamlined project setup.
  - Utilizes Vue Router for effective navigation across components.
  - Implements Vuex for centralized state management of global variables.

### Other Technologies
- **Redis**: Serves as a message broker for effective communication.
- **Celery**: Enables the execution of asynchronous batch jobs.
- **SMTPLIB**: Utilized for sending emails.
- **MailHog**: Acts as a fake SMTP Server for testing purposes.
- **Requests**: Used for posting webhook requests to Google Chat.

## Database Schema Design

1. **User Table (user):**
   - `username` (PK, String): Unique identifier for users.
   - `password` (String): Ensures user authentication.
   - `email` (String): Captures user email information.
   - `role` (String, default="user"): Designates user roles.
   - `approved` (String, default="No"): Indicates approval status.
   - `last_login` (DateTime, nullable): Records the timestamp of the last login.
   - `orders` (Relationship with Order): Establishes a link with user orders.

2. **Category Table (category):**
   - `id` (PK, Integer, Autoincrement): Provides a unique identifier for categories.
   - `category_name` (String): Stores the name of product categories.
   - `products` (Relationship with Product): Defines the relationship with products.
   - `approved` (String, default="No"): Indicates approval status.

3. **Product Table (product):**
   - `productID` (PK, Integer, Autoincrement): Serves as a unique identifier for products.
   - `product_name` (String): Contains the name of the product.
   - `product_category` (String, FK to Category): Establishes a link to product categories.
   - `stock` (Integer): Represents the stock quantity of the product.
   - `price` (Float): Specifies the price of the product.
   - `expiry_date` (DateTime): Captures the expiry date of the product.
   - `timestamp` (DateTime, default=datetime.utcnow): Records the creation timestamp.

4. **Order Table (order):**
   - `id` (PK, Integer, Autoincrement): Provides a unique identifier for orders.
   - `username` (FK to User): Links the order to the respective user.
   - `amount` (Float): Indicates the total order amount.
   - `products` (String): Stores a serialized format of ordered products.
   - `timestamp` (DateTime, default=datetime.utcnow): Records the timestamp of the order.

## API Design

The API is segmented into four major sections:

1. **Products:** Supports CRUD operations and facilitates product purchases.
2. **Categories:** Manages CRUD operations and handles category approval requests.
3. **User:** Includes endpoints for user login and signup functionalities.
4. **Manager Requests:** Directs requests to the admin dashboard for processing and approval.

## Architecture and Features

The project is organized into two main segments:

- **Frontend:** Developed using Vue.js for a dynamic and interactive user interface.
- **Backend:** Utilizes Flask to handle server-side logic and database interactions.

### Implemented Features:

- **RBAC:** Enables user and manager signup and login, along with admin login functionality.
- **CRUD Operations:** Allows managers to perform CRUD operations for products, and admins for categories.
- **User Cart Management:** Users can maintain and checkout items in their carts.
- **Advanced Filters:** Supports product search based on name, category, expiry date, and price.
- **Batch Jobs:** Implements daily reminders via Google Chat and generates monthly activity reports.
- **Responsive Design:** Ensures a seamless user experience across various devices.
