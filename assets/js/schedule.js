(function () {
  "use strict";

  var FIELDS = {
    date: ["date"],
    presenter: ["presenter", "speaker", "who"],
    title: ["title", "paper", "paper_title", "topic"],
    authors: ["authors", "author"],
    venue: ["venue", "conference", "conf"],
    link: ["link", "url", "paper_link", "pdf", "material", "slides"],
    publish: ["publish", "published", "live", "show"]
  };

  var META_FIELDS = {
    semester_id: ["semester_id", "id"],
    semester: ["semester"],
    time: ["time"],
    coordinator: ["coordinator"],
    tab: ["tab", "sheet_tab"]
  };

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeHeader(header) {
    return String(header || "")
      .trim()
      .toLowerCase()
      .replace(/[\s-]+/g, "_")
      .replace(/[^a-z0-9_]/g, "");
  }

  function parseCsv(text) {
    var rows = [];
    var row = [];
    var field = "";
    var inQuotes = false;
    var src = String(text || "").replace(/^\uFEFF/, "");
    var i;
    var ch;
    var next;

    for (i = 0; i < src.length; i += 1) {
      ch = src[i];
      next = src[i + 1];
      if (inQuotes) {
        if (ch === '"' && next === '"') {
          field += '"';
          i += 1;
        } else if (ch === '"') {
          inQuotes = false;
        } else {
          field += ch;
        }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === ",") {
        row.push(field);
        field = "";
      } else if (ch === "\n") {
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
      } else if (ch !== "\r") {
        field += ch;
      }
    }

    if (field.length || row.length) {
      row.push(field);
      rows.push(row);
    }

    return rows.filter(function (cells) {
      return cells.some(function (cell) {
        return String(cell).trim() !== "";
      });
    });
  }

  function mapHeaders(headers, aliases) {
    var mapped = {};
    headers.forEach(function (raw, idx) {
      var key = normalizeHeader(raw);
      Object.keys(aliases).forEach(function (field) {
        if (mapped[field] == null && aliases[field].indexOf(key) !== -1) {
          mapped[field] = idx;
        }
      });
    });
    return mapped;
  }

  function isHttpUrl(url) {
    try {
      var parsed = new URL(url);
      return parsed.protocol === "http:" || parsed.protocol === "https:";
    } catch (err) {
      return false;
    }
  }

  function renderRow(session) {
    var authors = session.authors
      ? '<p class="cell-authors">' + escapeHtml(session.authors) + "</p>"
      : "";
    var venue = session.venue
      ? '<span class="cell-venue">' + escapeHtml(session.venue) + "</span>"
      : "";
    var link = session.link && isHttpUrl(session.link)
      ? '<a class="cell-link" href="' + escapeHtml(session.link) + '" target="_blank" rel="noopener">' +
        '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm-1 7V3.5L18.5 9Z"/></svg>' +
        "Paper</a>"
      : "";

    return (
      "<tr>" +
        '<td class="col-date"><span class="cell-date">' + escapeHtml(session.date) + "</span></td>" +
        '<td class="col-presenter"><span class="cell-presenter">' + escapeHtml(session.presenter) + "</span></td>" +
        '<td class="col-title"><p class="cell-title">' + escapeHtml(session.title) + "</p>" + authors + "</td>" +
        '<td class="col-venue">' + venue + "</td>" +
        '<td class="col-material">' + link + "</td>" +
      "</tr>"
    );
  }

  function looksLikeHtmlLogin(text) {
    return /<html/i.test(text) && /sign in/i.test(text);
  }

  async function fetchCsv(url) {
    var response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      throw new Error("sheet fetch failed: " + response.status);
    }
    var text = await response.text();
    if (looksLikeHtmlLogin(text)) {
      throw new Error("sheet is not publicly readable");
    }
    return text;
  }

  function buildUrls(cfg) {
    var urls = [];
    var base;
    var gid;

    if (cfg.csv) {
      urls.push(cfg.csv);
    }

    if (cfg.id) {
      base = "https://docs.google.com/spreadsheets/d/" + encodeURIComponent(cfg.id);
      if (cfg.tab) {
        urls.push(base + "/gviz/tq?tqx=out:csv&sheet=" + encodeURIComponent(cfg.tab));
      }
      gid = cfg.gid || (cfg.tab ? "" : "0");
      if (gid !== "") {
        urls.push(base + "/gviz/tq?tqx=out:csv&gid=" + encodeURIComponent(gid));
        urls.push(base + "/export?format=csv&gid=" + encodeURIComponent(gid));
      }
    }

    return urls;
  }

  function rowsToObjects(rows, aliases) {
    var index = mapHeaders(rows[0] || [], aliases);
    return rows.slice(1).map(function (row) {
      var item = {};
      Object.keys(aliases).forEach(function (field) {
        var idx = index[field];
        item[field] = idx == null ? "" : String(row[idx] || "").trim();
      });
      return item;
    });
  }

  function isPublished(value) {
    var normalized = String(value || "").trim().toLowerCase();
    return normalized === "true" ||
      normalized === "yes" ||
      normalized === "y" ||
      normalized === "1" ||
      normalized === "x" ||
      normalized === "publish" ||
      normalized === "published" ||
      normalized === "checked";
  }

  function rowsToSessions(rows) {
    var index = mapHeaders(rows[0] || [], FIELDS);
    if (index.date == null && index.title == null) {
      throw new Error("missing date/title columns");
    }

    return rows.slice(1).map(function (row) {
      function get(field) {
        var idx = index[field];
        return idx == null ? "" : String(row[idx] || "").trim();
      }
      return {
        date: get("date"),
        presenter: get("presenter"),
        title: get("title"),
        authors: get("authors"),
        venue: get("venue"),
        link: get("link"),
        publish: get("publish"),
        hasPublish: index.publish != null
      };
    }).filter(function (session) {
      if (!(session.date || session.title || session.presenter)) {
        return false;
      }
      return !session.hasPublish || isPublished(session.publish);
    });
  }

  function setStatus(el, text, live) {
    if (!el) {
      return;
    }
    el.hidden = !text;
    el.textContent = text || "";
    el.classList.toggle("schedule-live--on", Boolean(live));
  }

  function applySemesterMeta(cfg, text) {
    var rows = rowsToObjects(parseCsv(text), META_FIELDS);
    var match = rows.filter(function (row) {
      return (cfg.semesterId && row.semester_id === cfg.semesterId) ||
        (cfg.tab && row.tab === cfg.tab);
    })[0];
    var timeChip;
    var timeText;
    var coordChip;
    var coordText;

    if (!match) {
      return;
    }

    timeChip = document.querySelector("[data-hero-time]");
    timeText = document.querySelector("[data-hero-time-text]");
    if (match.time && timeText) {
      timeText.textContent = match.time;
      if (timeChip) {
        timeChip.hidden = false;
      }
    }

    coordChip = document.querySelector("[data-hero-coordinator]");
    coordText = document.querySelector("[data-hero-coordinator-text]");
    if (match.coordinator && coordText) {
      coordText.textContent = match.coordinator;
      if (coordChip) {
        coordChip.hidden = false;
      }
    }
  }

  async function fetchFirstCsv(urls) {
    var lastError = null;
    var i;
    for (i = 0; i < urls.length; i += 1) {
      try {
        return await fetchCsv(urls[i]);
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError || new Error("no sheet url");
  }

  async function loadSchedule(tbody) {
    var cfg = {
      id: (tbody.dataset.sheetId || "").trim(),
      tab: (tbody.dataset.sheetTab || "").trim(),
      gid: (tbody.dataset.sheetGid || "").trim(),
      csv: (tbody.dataset.sheetCsv || "").trim(),
      semesterId: (tbody.dataset.semesterId || "").trim()
    };
    var status = document.querySelector("[data-schedule-status]");
    var count = document.querySelector("[data-schedule-count]");
    var urls = buildUrls(cfg);
    var sessions;

    if (!urls.length) {
      return;
    }

    setStatus(status, "Updating from Google Sheet…", false);
    if (cfg.id) {
      fetchFirstCsv(buildUrls({ id: cfg.id, tab: "Semesters" }))
        .then(function (text) {
          applySemesterMeta(cfg, text);
        })
        .catch(function (err) {
          console.warn("Reading group schedule: semester metadata unavailable.", err);
        });
    }

    try {
      sessions = rowsToSessions(parseCsv(await fetchFirstCsv(urls)));
    } catch (err) {
      setStatus(status, "Showing saved schedule", false);
      console.warn("Reading group schedule: using saved fallback.", err);
      return;
    }

    tbody.innerHTML = sessions.length
      ? sessions.map(renderRow).join("")
      : '<tr><td class="schedule-empty" colspan="5">No published sessions yet.</td></tr>';
    if (count) {
      count.textContent = sessions.length + (sessions.length === 1 ? " session" : " sessions");
    }
    setStatus(status, "Live from Google Sheet", true);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var tbody = document.querySelector("[data-schedule-sheet]");
    if (tbody) {
      loadSchedule(tbody);
    }
  });
})();
