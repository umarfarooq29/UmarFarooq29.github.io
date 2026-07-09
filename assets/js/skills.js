(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };

  var fallbackSkills = [
    {
      category: "Analytics",
      summary: "Turning raw data into readable decisions.",
      items: [
        { name: "Statistics", level: 92 },
        { name: "Python", level: 88 },
        { name: "SQL", level: 84 },
        { name: "Power BI", level: 82 },
        { name: "Excel", level: 86 },
        { name: "Data visualization", level: 88 },
      ],
    },
    {
      category: "Data Science",
      summary: "Building clean workflows for modeling and insight.",
      items: [
        { name: "Machine learning", level: 80 },
        { name: "Data cleaning", level: 90 },
        { name: "Exploratory analysis", level: 88 },
        { name: "Forecasting", level: 76 },
        { name: "Pandas", level: 86 },
        { name: "NumPy", level: 82 },
      ],
    },
    {
      category: "Development",
      summary: "Designing responsive mobile and web experiences.",
      items: [
        { name: "Flutter", level: 84 },
        { name: "Dart", level: 80 },
        { name: "Firebase", level: 76 },
        { name: "Git", level: 82 },
        { name: "Responsive UI", level: 88 },
        { name: "REST APIs", level: 78 },
      ],
    },
  ];

  function normalizeSkills(data) {
    if (Array.isArray(data)) {
      return data
        .map(function (group) {
          return {
            category: group.category || group.title || "Skills",
            summary: group.summary || "",
            items: Array.isArray(group.items) ? group.items : Array.isArray(group.skills) ? group.skills : [],
          };
        })
        .filter(function (group) {
          return group.items.length;
        });
    }

    if (data && typeof data === "object") {
      return Object.keys(data).map(function (key) {
        var value = data[key];
        return {
          category: key,
          summary: value && value.summary ? value.summary : "",
          items: Array.isArray(value) ? value : value && Array.isArray(value.items) ? value.items : [],
        };
      }).filter(function (group) {
        return group.items.length;
      });
    }

    return [];
  }

  function normalizeSkillItem(item) {
    if (typeof item === "string") {
      return {
        name: item,
        level: null,
      };
    }

    return {
      name: item.name || item.title || "Skill",
      level: Number.isFinite(Number(item.level)) ? Math.max(0, Math.min(100, Number(item.level))) : null,
    };
  }

  function createSkillItem(item) {
    var skill = normalizeSkillItem(item);
    var listItem = document.createElement("li");
    var skillName = document.createElement("span");

    listItem.className = "skill-item";
    skillName.className = "badge-soft";
    skillName.textContent = skill.name;
    listItem.appendChild(skillName);

    if (skill.level !== null) {
      var meter = document.createElement("span");
      var bar = document.createElement("span");

      meter.className = "skill-meter";
      meter.setAttribute("aria-hidden", "true");
      bar.style.width = skill.level + "%";
      meter.appendChild(bar);
      listItem.appendChild(meter);
    }

    return listItem;
  }

  function createSkillCard(group, index) {
    var article = document.createElement("article");
    var heading = document.createElement("h3");
    var list = document.createElement("ul");

    article.className = "skill-card soft-card";
    article.setAttribute("data-reveal", "");
    article.style.setProperty("--reveal-delay", index * 90 + "ms");

    heading.textContent = group.category;
    article.appendChild(heading);

    if (group.summary) {
      var summary = document.createElement("p");
      summary.className = "skill-summary";
      summary.textContent = group.summary;
      article.appendChild(summary);
    }

    list.className = "skill-tags skill-tags--enhanced";
    list.setAttribute("aria-label", group.category + " skills");

    group.items.forEach(function (item) {
      list.appendChild(createSkillItem(item));
    });

    article.appendChild(list);
    return article;
  }

  function renderSkills(container, groups) {
    var fragment = document.createDocumentFragment();

    container.textContent = "";

    groups.forEach(function (group, index) {
      fragment.appendChild(createSkillCard(group, index));
    });

    container.appendChild(fragment);

    if (app.observeReveals) {
      app.observeReveals(container);
    }

    window.dispatchEvent(new CustomEvent("portfolio:contentchange", {
      detail: {
        source: "skills",
      },
    }));
  }

  function loadSkills() {
    if (!window.fetch) {
      return Promise.resolve(fallbackSkills);
    }

    return fetch("data/skills.json", {
      cache: "no-store",
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Unable to load skills data");
        }

        return response.text();
      })
      .then(function (text) {
        var trimmed = text.trim();
        var parsed = trimmed ? JSON.parse(trimmed) : fallbackSkills;
        var normalized = normalizeSkills(parsed);

        return normalized.length ? normalized : fallbackSkills;
      })
      .catch(function () {
        return fallbackSkills;
      });
  }

  ready(function () {
    var container = document.querySelector("[data-skills-grid]");

    if (!container) {
      return;
    }

    loadSkills().then(function (groups) {
      renderSkills(container, groups);
    });
  });
})();
