Our courses contain interactive Codepen (codepen.io) embeds which allow our users a hands-on learning experience. Codepen allows us to embed working codepen editors in our course content, and these editors can facilitate Javascript, HTML, and CSS (as well as CSS variants, such as SCSS, etc). 

In order to accurately parse this information, we have developed custom Wordpress-like shortcodes for reading codepen embeds in our course content. We would ask that you abide by the following shortcode shape, as we will not be able to parse this information otherwise. 

<!-- Example CodePen Shortcode -->
[codepen]

[description]Description of the Codepen component.[/description]

[template lang="html"]
```html
<h1>Hello World!</h1>

<body>
  <button id="btn">Click me</button>
</body>
```
[/template]

[/styles lang="css"]
```css
body {
  background-color: blue;
}
```
[/styles]

[scripts lang="javascript"]
```javascript
document.getElementsByTagName("h1")[0].style.fontSize = "80px";
```
[/scripts]

[dependency]https://link-to-dependency-or-dependency-name/dependency.min.js[/dependency]

[/codepen]

<!-- End Example CodePen Shortcode -->


Shortcode Rules:
- Attempt to link to a working dependency link in the dependency field, but it is not important if you simply add the name of a dependency instead of a link. 

