# from revChatGPT.V3 import Chatbot
import openai
import openai.error as oe
from typing import Literal
import os, os.path
import json
from pathlib import Path


resolutions = Literal["256", "512"]


class InvalidRequest(Exception):
    pass


SYSTEM_PROMPT = """Ты играешь роль девушки помощницы на сервере Japit Comics в Discord. Ты не имеешь прав на сервере, ты можешь только отвечать на вопросы людей. Если ты не знаешь ответ, не придумывай его, скажи, что не знаешь ответ. При невозможности выполнить запрос, вежливо откажи."""


def fix_markdown(text: str) -> str:
    if text.count("```") % 2 != 0:
        return f"{text}\n```"
    else:
        return text


# MRKD_LANG_LIST = ["```python", "```swift", "```c++", "```csharp", "```c", "```rust", "```javascript", "```typescript", "```fortran", "```html", "```php", "```sql"]


class ChatGPT:
    def __init__(self, oaitoken) -> None:
        self.oaitoken = oaitoken
        self.conversations = {}
        for item in os.listdir("./chats/"):
            with open(f"./chats/{item}", encoding="utf-8") as file:
                self.conversations.update({item.replace(".json", ""): json.load(file)})

    def add_to_conversation(self, convo_id: str, author: str, text: str) -> None:
        text_dict = {"role": author, "content": text}

        if not os.path.isfile(path=f"./chats/{convo_id}.json"):  # проверяет json с историей сообщений для конкретного канала. если его нет, создает и грузит в память
            obj = {"messages": [{"role": "system", "content": SYSTEM_PROMPT}]}
            self.conversations.update({convo_id: obj})

        self.conversations[convo_id]["messages"].append(text_dict)
        with open(f"./chats/{convo_id}.json", "w", encoding="utf-8") as file:
            json.dump(self.conversations[convo_id], file, indent=4, ensure_ascii=False)

    async def fake_chat_completion(self, prompt: str, convo_id="1093166962428882996", selection: int = 1) -> str:
        match selection:
            case 1:
                return "nigga penis\n```python\ndef nigas():\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\nprint('CUM')\n```"

            case 2:
                return 'Ниже приведен пример экрана регистрации на UIKit swift, который сверстан без использования IBOutlet\'тов:\n\n```swift\nimport UIKit\n\nclass RegistrationViewController: UIViewController {\n\n    let emailTextField: UITextField = {\n        let textField = UITextField()\n        textField.placeholder = "Email"\n        textField.borderStyle = .roundedRect\n        textField.textAlignment = .center\n        textField.translatesAutoresizingMaskIntoConstraints = false\n        return textField\n    }()\n\n    let passwordTextField: UITextField = {\n        let textField = UITextField()\n        textField.placeholder = "Password"\n        textField.isSecureTextEntry = true\n        textField.borderStyle = .roundedRect\n        textField.textAlignment = .center\n        textField.translatesAutoresizingMaskIntoConstraints = false\n        return textField\n    }()\n\n    let confirmPasswordTextField: UITextField = {\n        let textField = UITextField()\n        textField.placeholder = "Confirm Password"\n        textField.isSecureTextEntry = true\n        textField.borderStyle = .roundedRect\n        textField.textAlignment = .center\n        textField.translatesAutoresizingMaskIntoConstraints = false\n        return textField\n    }()\n\n    let registerButton: UIButton = {\n        let button = UIButton(type: .system)\n        button.setTitle("Register", for: .normal)\n        button.titleLabel?.font = UIFont.boldSystemFont(ofSize: 16)\n        button.setTitleColor(.white, for: .normal)\n        button.backgroundColor = .systemBlue\n        button.layer.cornerRadius = 5\n        button.translatesAutoresizingMaskIntoConstraints = false\n        return button\n    }()\n\n    override func viewDidLoad() {\n        super.viewDidLoad()\n\n        view.backgroundColor = .white\n\n        let fieldsStackView = UIStackView(arrangedSubviews: [emailTextField, passwordTextField, confirmPasswordTextField])\n        fieldsStackView.axis = .vertical\n        fieldsStackView.distribution = .fillEqually\n        fieldsStackView.spacing = 10\n        fieldsStackView.translatesAutoresizingMaskIntoConstraints = false\n\n        view.addSubview(fieldsStackView)\n        view.addSubview(registerButton)\n\n        NSLayoutConstraint.activate([\n            fieldsStackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),\n            fieldsStackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),\n            fieldsStackView.centerYAnchor.constraint(equalTo: view.centerYAnchor),\n            fieldsStackView.heightAnchor.constraint(equalToConstant: 150),\n\n            registerButton.topAnchor.constraint(equalTo: fieldsStackView.bottomAnchor, constant: 20),\n            registerButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),\n            registerButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),\n            registerButton.heightAnchor.constraint(equalToConstant: 50)\n        ])\n    }\n}\n```\n\nЭтот код создает экран регистрации со всеми необходимыми элементами, такими как поля для ввода адреса электронной почты и пароля, кнопка для отправки регистрационных данных и т.д. Все элементы расположены в StackView, чтобы быть выровненными и гибкими на разных устройствах. Без использования IBOutlet\'тов мы можем управлять всеми элементами через код, что может быть полезно в случае, если вы хотите создать гибкий и легко настраиваемый интерфейс для пользователей.'

            case 3:
                return """Lo\nrem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse ornare odio eu enim vestibulum lobortis sit amet nec dolor. Duis ut velit ex. Nullam sagittis hendrerit luctus. Sed quis laoreet erat. Aenean convallis tortor nonvelit ornare scelerisque. Nam congue quam nec mi sagittis, ut semper leo efficitur. Morbi sodales varius tellus, vitae maximus quam tincidunt cursus. Morbi malesuada aliquet convallis. Suspendisse pharetra, arcu ut bibendum pharetra, diam turpis lobortis justo, in dignissim dolor mi sit amet turpis. Nulla vel turpis ultrices, porttitor nisi a, fringilla tortor. Quisque molestie tellus sed arcu porttitor aliquet. Mauris sodales augue justo, a dignissim elit sagittis et. Integer et dictum turpis. Maecenas egestas in nibh sed volutpat. Integer ullamcorper pulvinar porttitor. Maecenas tristique sed justo id tincidunt. Donec facilisis viverra elit. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Suspendisse ut velit eu turpis semper ullamcorper. Ut ex libero, consectetur porttitor odio id, rhoncus congue diam. In vel laoreet magna. In aliquam non arcu ut pulvinar. Donec fermentum massa eros, ut tincidunt libero sodales sit amet. Vivamus consectetur efficitur urna, sit amet finibus sapien. Fusce id erat a leo vulputate suscipit vel vel magna. Nunc eu semper massa. Pellentesque non enim sed velit fringilla sagittis quis vel elit. Maecenas eu lacus est. Fusce arcu quam, scelerisque nec felis at, egestas fermentum ligula. Maecenas scelerisque diam ligula, eget ornare lectus vestibulum sit amet. Sed non mauris finibus, finibus sem a, faucibus ante. Etiam id diam vel turpis mattis hendrerit. Proin sed magna volutpat, aliquam massa quis, molestie neque. Aliquam eu pellentesque magna. Donec cursus, risus et iaculis congue, enim risus euismod urna, quis sagittis tortor sapien nec tortor. Suspendisse at lacinia neque. Etiam finibus lobortis pulvinar. Duis et massa eget libero luctus faucibus sed eget sem. Sed ut tristique nunc. Maecenas sed cursus turpis, et convallis augue. Suspendisse nec velit ac purus vulputate viverra sit amet sit amet eros. Maecenas tristique dui quam, ut lacinia est condimentum id. Quisque at varius odio, eleifend lacinia turpis. In a rutrum magna. Sed ac ipsum nec metus egestas rutrum quis non nisl. Nunc efficitur risus sit amet tortor consectetur varius. uisque et pharetra ante. Quisque sollicitudin risus ligula, id feugiat metus efficitur id. Maecenas vel dui elit. Praesent sed ante tempus sapien porttitor laoreet nec in nibh. Nulla viverra vitae enim a faucibus. Mauris efficitur odio felis, eu scelerisque velit viverra sed. Proin luctus libero nunc, sit amet condimentum magna porttitor a. Nam hendrerit volutpat nisi eu laoreet. Nam eu magna sit amet elit viverra rhoncus. Nunc pharetra ut purus in iaculis. Aenean dictum venenatis sapien, et imperdiet ante ultricies eget. Ut quis ornare lacus. Proin elementum justo a tempus gravida. Nulla fringilla, sem nec dictum eu. """

            case 4:
                return """Без проблем! Ниже представлены еще 10 примеров псевдокода на Python:\n\n1. Пример псевдокода на Python для вычисления фибоначчиева числа:\n\n```python\n# Входное число n\nn = 8\n\n# Вычисление фибоначчиева числа\na, b = 0, 1\nfor i in range(n):\n    a, b = b, a + b\n\n# Вывод результата\nprint(\"Фибоначчиево число: \" + str(a))\n```\n\n2. Пример псевдокода на Python для нахождения корней квадратного уравнения:\n\n```python\n# Входные данные\na = 2\nb = -1\nc = -6\n\n# Вычисление корней квадратного уравнения\nimport math\ndiscriminant = b**2 - 4*a*c\nif discriminant < 0:\n    print(\"Корней нет\")\nelif discriminant == 0:\n    x = -b / (2*a)\n    print(\"Один корень: \" + str(x))\nelse:\n    x1 = (-b + math.sqrt(discriminant)) / (2*a)\n    x2 = (-b - math.sqrt(discriminant)) / (2*a)\n    print(\"Два корня: \" + str(x1) + \" и \" + str(x2))\n```\n\n3. Пример псевдокода на Python для суммирования элементов двумерного массива:\n\n```python\n# Входной двумерный массив\nmatrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n\n# Суммирование элементов двумерного массива\nsum_of_elements = 0\nfor row in matrix:\n    for element in row:\n```\n        sum_of_elements += element \nLorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse ornare odio eu enim vestibulum lobortis sit amet nec dolor. Duis ut velit ex. Nullam sagittis hendrerit luctus. Sed quis laoreet erat. Aenean convallis tortor nonvelit ornare scelerisque. Nam congue quam nec mi sagittis, ut semper leo efficitur. Morbi sodales varius tellus, vitae maximus quam tincidunt cursus. Morbi malesuada aliquet convallis. Suspendisse pharetra, arcu ut bibendum pharetra, diam turpis lobortis justo, in dignissim dolor mi sit amet turpis. Nulla vel turpis ultrices, porttitor nisi a, fringilla tortor. Quisque molestie tellus sed arcu porttitor aliquet. Mauris sodales augue justo, a dignissim elit sagittis et. Integer et dictum turpis. Maecenas egestas in nibh sed volutpat. Integer ullamcorper pulvinar porttitor. Maecenas tristique sed justo id tincidunt. Donec facilisis viverra elit. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Suspendisse ut velit eu turpis semper ullamcorper. Ut ex libero, consectetur porttitor odio id, rhoncus congue diam. In vel laoreet magna. In aliquam non arcu ut pulvinar. Donec fermentum massa eros, ut tincidunt libero sodales sit amet. Vivamus consectetur efficitur urna, sit amet finibus sapien."""

            case _:
                return prompt

    async def chat_completion(self, prompt: str, convo_id="1093166962428882996") -> str:
        openai.api_key = self.oaitoken
        self.add_to_conversation(convo_id, "user", prompt)
        messages = self.conversations[convo_id]["messages"][-15:]
        try:
            text = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=messages)
            self.add_to_conversation(convo_id, "assistant", text.choices[0].message["content"])  # type: ignore
            return str(text.choices[0].message["content"])  # type: ignore
        except Exception as e:
            return f"{e.__class__.__name__} {e}"

    async def generate_image(self, prompt: str, resolution) -> str:
        if self.oaitoken is None:
            raise Exception

        try:
            image_url = await openai.Image.acreate(
                api_key=self.oaitoken,
                prompt=prompt,
                n=1,
                size=f"{resolution}x{resolution}",
            )
            return image_url["data"][0]["url"]  # type:ignore
        except oe.InvalidRequestError:
            print("InvalidRequestError: Your request was rejected as a result of our safety system. Your prompt may contain text that is not allowed by our safety system.")
            raise InvalidRequest
        except Exception as e:
            print(e.__class__.__name__, e)
            text = "exception"
            return text
