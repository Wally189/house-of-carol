(function () {
  var root = document.documentElement;
  var storageKey = "waylight-template-theme";
  var themes = ["red", "yellow", "pink", "green", "purple", "orange", "blue", "cream", "black"];
  var labels = {
    red: "Red",
    yellow: "Yellow",
    pink: "Pink",
    green: "Green",
    purple: "Purple",
    orange: "Orange",
    blue: "Blue",
    cream: "Cream",
    black: "Black"
  };
  var legacyThemes = {
    atlantic: "blue",
    heather: "green",
    sand: "cream"
  };

  function normalizeTheme(theme) {
    var value = legacyThemes[theme] || theme;
    return themes.indexOf(value) >= 0 ? value : "blue";
  }

  function applyTheme(theme, options) {
    var value = normalizeTheme(theme);
    var persist = !options || options.persist !== false;
    root.setAttribute("data-theme", value);

    if (persist) {
      try {
        window.localStorage.setItem(storageKey, value);
      } catch (error) {
        // Ignore storage failures and keep the current in-memory theme.
      }
    }

    var text = labels[value];
    document.querySelectorAll("[data-theme-label]").forEach(function (node) {
      node.textContent = text;
    });
  }

  function nextTheme(currentTheme) {
    var index = themes.indexOf(currentTheme);
    return themes[(index + 1) % themes.length];
  }

  var initialTheme = normalizeTheme(root.getAttribute("data-theme") || "blue");
  try {
    initialTheme = window.localStorage.getItem(storageKey) || initialTheme;
  } catch (error) {
    initialTheme = normalizeTheme(root.getAttribute("data-theme") || "blue");
  }

  applyTheme(initialTheme, { persist: false });

  document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      var activeTheme = normalizeTheme(root.getAttribute("data-theme") || "blue");
      applyTheme(nextTheme(activeTheme), { persist: true });
    });
  });
})();
