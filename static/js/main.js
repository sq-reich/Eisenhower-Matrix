$(function () {
  const $customSelect = $("#customPriority");
  const $optionsList = $customSelect.next(".select-options");
  const $hiddenInput = $("#priority");
  const $selectedSpan = $customSelect.find(".selected");

  $customSelect.on("click", function (e) {
    e.stopPropagation();
    const expanded = $(this).attr("aria-expanded") === "true";
    $(this).attr("aria-expanded", !expanded);
  });

  $(document).on("click", function () {
    $customSelect.attr("aria-expanded", "false");
  });

  $optionsList.find("li").on("click", function () {
    const value = $(this).data("value");
    const text = $(this).text();

    $optionsList.find("li").removeClass("selected").removeAttr("aria-selected");
    $(this).addClass("selected").attr("aria-selected", "true");

    $selectedSpan.text(text);
    $hiddenInput.val(value);
    $customSelect.attr("aria-expanded", "false");
  });

  $customSelect.on("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      const expanded = $(this).attr("aria-expanded") === "true";
      $(this).attr("aria-expanded", !expanded);
    }
  });

  $(".edit-toggle").click(function () {
    const $card = $(this).closest(".todo-card");
    $card.find(".edit-form").removeClass("d-none");
  });

  $(".cancel-edit").click(function () {
    $(this).closest(".edit-form").addClass("d-none");
  });

  $(".todo-actions a.btn-outline-success").on("click", function (e) {
    e.preventDefault();

    const $btn = $(this);
    const $card = $btn.closest(".todo-card");
    const todoId = $btn.attr("href").split("/").pop();
    const $title = $card.find(".todo-title-text");
    const $statusBadge = $card.find(".status-badge");
    const $icon = $btn.find("i");

    $.ajax({
      url: `/update/${todoId}`,
      method: "POST",
      data: {},
      success: function (response) {
        if (response.complete) {
          $icon
            .removeClass("fa-check")
            .addClass("fa-times")
            .fadeOut(150)
            .fadeIn(150);
          $statusBadge
            .removeClass("bg-secondary")
            .addClass("bg-success")
            .html('<i class="fas fa-check"></i> Erledigt')
            .hide()
            .fadeIn(300);

          $title.animate({ opacity: 0.5 }, 200, function () {
            $title.addClass("strikethrough");
            $title.animate({ opacity: 1 }, 300);
          });
        } else {
          $icon
            .removeClass("fa-times")
            .addClass("fa-check")
            .fadeOut(150)
            .fadeIn(150);
          $statusBadge
            .removeClass("bg-success")
            .addClass("bg-secondary")
            .text("⏳ Offen")
            .hide()
            .fadeIn(300);

          $title.animate({ opacity: 0.5 }, 200, function () {
            $title.removeClass("strikethrough");
            $title.animate({ opacity: 1 }, 300);
          });
        }
      },
      error: function () {
        alert("Fehler beim Aktualisieren des Status.");
      },
    });
  });
});

/* ===== Loader Script ====== */
window.addEventListener("load", () => {
  const overlay = document.getElementById("loader");
  if (overlay) {
    setTimeout(() => {
      overlay.style.display = "none";
    }, 1500);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
  });
  calendar.render();
});
