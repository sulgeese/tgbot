function format_date(dateStr) {

  const date = new Date(dateStr);

  const timeHTML = `
    <div class="time">
      ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}
    </div>
  `;

  const weekday = date.toLocaleDateString('ru-RU', { weekday: 'long'});
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();

  const dateHTML = `
    <div class="date">
      ${weekday.charAt(0).toUpperCase() + weekday.slice(1)}, ${day}.${month}.${year}
    </div>
  `;

  return timeHTML + dateHTML;

}