/**
 * Sample React component with code quality issues
 */

// Unclear variable naming
function component(props) {
  const a = props.data;
  const b = a.map(x => x * 2);
  
  // Direct DOM manipulation instead of state
  const el = document.getElementById('result');
  
  // No error handling
  const response = fetch('/api/data');
  const json = response.json();
  
  // God component doing too much
  function process(input) {
    const v1 = validate(input);
    const v2 = transform(v1);
    const v3 = save(v2);
    const v4 = notify(v3);
    return v4;
  }
  
  // Missing prop types validation
  return (
    <div>
      {b.map(item => <span>{item}</span>)}
    </div>
  );
}

export default component;
