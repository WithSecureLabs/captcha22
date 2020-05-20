
First of all, thanks for getting involved!

## Feature structure

Features are provided in the form of a script in the lib section. To ensure that your feature can be integrated, please build a class that supports arguments and default parameters. Please choose the directory that fits your feature the best:

| Directory  | Description                                                    |
| ---------- | -------------------------------------------------------------- |
| `api`      | Scripts used for server and client API features                |
| `core`     | Primary imports of both client and server features             |
| `crackers` | Cracker scripts to automate attacks once the CAPTCHA is solved |
| `labels`   | Scripts to make the labelling process easier                   | 
| `server`   | Primary CAPTCHA cracking engine scripts                        |

## Adding a feature

1. Create a class of your feature and select the directory that first you features the best. 
2. Update either the server or client `core` script by adding a function that can import and call your class.
3. Update `__main__.py` to include arguments for your feature as well as the corresponding `core` function.
4. If you with to expose your feature to further development, include the class in the `__init__.py` file.
5. Submit a Pull Request to the master branch.

## Documentation

We're well aware there is a lot we haven't documented. This is something we plan on rectifying by putting together a new wiki. For now, please feel free to use the Github issue tracker for any questions. 

## Future ideas and wishlist

The following is a list of the features we are looking to provide in the future:

* Logging support to enable both interactive and silent modes on the API.
* Better parameter tweaking on the CAPTCHA training process.
* More generic cracker templates for easier integration.
* Automating client-side model hosting.
* WebGUI to interface with API.
