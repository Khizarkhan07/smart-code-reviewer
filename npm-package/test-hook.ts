// Quick test file to trigger pre-commit hook
function getData(x: any) {
  var result = fetch("/api/" + x);
  var d = result;
  console.log(d);
  return d;
}
export default getData;
