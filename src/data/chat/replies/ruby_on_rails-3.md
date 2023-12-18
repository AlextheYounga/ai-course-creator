# Lesson 3: Setting Up the Development Environment

Before you can start building Ruby on Rails applications, you need to set up your development environment. In this lesson, we will guide you through the steps of installing Ruby on Rails and introduce you to some basic terminal commands that you'll need as a Rails developer.

## Installing Ruby on Rails

To install Ruby on Rails on your machine, follow these steps:

1. **Install Ruby**: Visit the [Ruby Downloads](https://www.ruby-lang.org/en/downloads/) page and select the appropriate installer for your operating system. Follow the installation instructions provided.

2. **Install Rails**: Once Ruby is installed, open your terminal and execute the following command:

   ```bash
   gem install rails
   ```

   This command will install the latest version of Rails. You can verify the installation by running:

   ```bash
   rails -v
   ```

   If you see the Rails version printed in the terminal, it means Rails is successfully installed.

3. **Install Node.js and Yarn**: Rails uses Node.js and Yarn for managing JavaScript assets and dependencies. Visit the [Node.js](https://nodejs.org/en/) website and download the installer for your operating system. Follow the installation instructions. After installing Node.js, execute the following command to install Yarn:

   ```bash
   npm install -g yarn
   ```

   This command will install Yarn globally on your machine.

## Basic Terminal Commands

As a Rails developer, you'll frequently work with the terminal. Here are some essential terminal commands that will help you navigate your Rails projects:

- `cd`: Change directory. Use this command followed by the directory path to navigate to a specific folder.
- `ls`: List files and directories in the current directory.
- `mkdir`: Create a new directory. Follow this command with the desired directory name to create a new folder.
- `touch`: Create a new file. Specify the file name after the `touch` command to create a new file in the current directory.
- `ruby`: Execute a Ruby script. Use this command followed by the script file name to run Ruby code.
- `rails`: Execute Rails commands. Prefix various commands such as `generate`, `migrate`, and `server` with `rails` to perform specific actions within your Rails application.

## Conclusion

In this lesson, you learned how to set up your development environment by installing Ruby on Rails and familiarizing yourself with basic terminal commands. Having a properly configured development environment is crucial for efficient Rails development.

In the next lesson, we will explore the MVC architecture and understand how Rails utilizes this architectural pattern to structure web applications.