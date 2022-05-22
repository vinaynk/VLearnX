//
// based on chess_knight_journey.py
//

#include <iostream>
#include <vector>


using std::vector;
using std::cout;
using std::endl;


template <typename T>
struct Point {
  T x;
  T y;

  Point(T x_=0, T y_=0) {
    x = x_;
    y = y_;
  }

  Point
  add(Point &p) {
    return Point(x + p.x, y + p.y);
  }

};


using PointI = Point<int>;


class SearchEnvFullBoard {

  vector<PointI> _jumpNextSteps;

  int _size = 0;

  vector<bool> _marks;

  bool _log = false;

  int _limit = (int) 1E8;

  vector<PointI>
  createJumpNextSteps() {
    vector<PointI> vec = { {1, 2}, {2, 1} };
    // flip wrt x axis
    int size = vec.size();
    for (int idx = 0; idx < size; idx++) {
      auto point = vec[idx];
      vec.push_back({point.x, -point.y});
    }
    // flip wrt y axis
    size = vec.size();
    for (int idx = 0; idx < size; idx++) {
      auto point = vec[idx];
      vec.push_back({-point.x, point.y});
    }
    return vec;
  }

public:

  bool found = false;

  int njumps = 0;

  vector<PointI> path;

  SearchEnvFullBoard(int size, bool log, int limit=1E8) {
    _limit = limit;
    _log   = log;
    _size  = size;
    _marks = vector<bool>(size*size);
    _jumpNextSteps = createJumpNextSteps();
  }


  int
  getIdx(PointI &p) {
    return p.x * _size + p.y;
  }


  bool
  isMarked(PointI &p) {
    return _marks[getIdx(p)];
  }


  void
  push(PointI &p) {
    _marks[getIdx(p)] = true;
    njumps++;
    path.push_back(p);
    if ((njumps % 10000000 == 0) && _log) {
      cout << "at: " << njumps << endl;
    }
  }


  void
  pop() {
    auto p = path.back();
    path.pop_back();
    _marks[getIdx(p)] = false;
  }


  int
  remaining() {
    return _size * _size - path.size();
  }


  vector<PointI>
  possibleJumps(PointI &p) {
    vector<PointI> ret;
    for (auto &q : _jumpNextSteps) {
      auto r = p.add(q);
      if ((r.x >= 0) && (r.x < _size) &&
          (r.y >= 0) && (r.y < _size)) {
        ret.push_back(r);
      }
    }
    return ret;
  }


  bool
  limitReached() {
    return njumps > _limit;
  }

};


void
knightWalk(PointI &p, SearchEnvFullBoard &env) {

  env.push(p);

  if (env.limitReached()) {
    return;
  }

  if (env.remaining() == 0) {
    env.found = true;
    return;
  }

  auto jumps = env.possibleJumps(p);

  for (auto &jump : jumps) {
    if (env.found) {
      break;
    }
    if (env.isMarked(jump)) {
      continue;
    }
    knightWalk(jump, env);
  }

  if (!env.found) {
    env.pop();
  }

}


int
main(int argc, char* argv[]) {
  (void) argc;
  (void) argv;

  int size = 8;
  for (int ii = 0; ii < size; ii++) {
    for (int jj = 0; jj < size; jj++) {
      cout << "--" << endl;
      cout << "Start: " << ii << "," << jj << endl;
      SearchEnvFullBoard env(size, true);
      PointI start {ii, jj};
      knightWalk(start, env);
      if (env.found) {
        cout << "Total jumps: " << env.njumps << endl;
        for (auto &p : env.path) {
          cout << p.x << "," << p.y << "  ";
        }
        cout << endl;
      } else {
        cout << "search failed!" << endl;
      }
    }
  }

  return 0;
}


