Codepen (codepen.io) allows us to embed Codepen editors on our website. Codepen allows for dynamic Javascript, HTML, and CSS (and CSS variants, such as SCSS, etc). 

<!-- Example CodePen Component -->
[codepen]

[description]Description of the Codepen component.[/description]

[template]
```html
<h1>Hello World!</h1>

<body>
  <button id="btn">Click me</button>
</body>
```
[/template]

[/styles]
```css
$blue: #a3d5d3;

body {
  background-color: $blue;
}
```
[/styles]

[scripts]
```javascript
document.getElementsByTagName("h1")[0].style.fontSize = "80px";
```
[/scripts]

[dependency]https://link-to-dependency-or-dependency-name/dependency.min.js[/dependency]

[/codepen]

<!-- End Example CodePen Component -->
>NOTE: Codepen components are not submittable, so these components will not require "answer" or "must-contain" fields.
>NOTE: Do your best with the dependency field, but it is not super important if you simply add the name of a dependency and not a direct cdn link.