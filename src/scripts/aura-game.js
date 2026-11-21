export const ARENA = {
	width: 32,
	height: 22,
	obstacles: [
		[8, 2, 2, 9],
		[8, 15, 2, 6],
		[15, 0, 2, 7],
		[15, 11, 2, 8],
		[22, 4, 2, 10],
		[25, 17, 5, 2],
	],
};

const START_CELL = [3, 3];
const TARGET_START_CELL = [28, 14];
const ROBOT_RADIUS = 0.36;
const TAG_DISTANCE = 0.78;
const ROBOT_SPEED = 7.6;
const TARGET_STEP_INTERVAL = 1 / ROBOT_SPEED;
const CHASE_TIME_LIMIT = 60;
const ORB_SPAWN_INTERVAL = 30;
const POWER_UP_DURATION = 5;
const ORB_PICKUP_DISTANCE = 0.65;
const DIRECTIONS = [
	[1, 0],
	[-1, 0],
	[0, 1],
	[0, -1],
];

const cellKey = ([x, y]) => `${x},${y}`;
const manhattan = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
const distanceSquared = (a, b) => (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export function cellToWorld([x, y]) {
	return {
		x: x - ARENA.width / 2 + 0.5,
		z: y - ARENA.height / 2 + 0.5,
	};
}

export function worldToCell({ x, z }) {
	return [
		clamp(Math.floor(x + ARENA.width / 2), 0, ARENA.width - 1),
		clamp(Math.floor(z + ARENA.height / 2), 0, ARENA.height - 1),
	];
}

function collidesWithObstacle(x, z, radius = ROBOT_RADIUS) {
	const minX = -ARENA.width / 2;
	const minZ = -ARENA.height / 2;
	for (const [gridX, gridY, width, height] of ARENA.obstacles) {
		const left = minX + gridX;
		const right = left + width;
		const top = minZ + gridY;
		const bottom = top + height;
		const nearestX = clamp(x, left, right);
		const nearestZ = clamp(z, top, bottom);
		if ((x - nearestX) ** 2 + (z - nearestZ) ** 2 < radius ** 2) {
			return true;
		}
	}
	return false;
}

function isBlocked([x, y]) {
	const point = cellToWorld([x, y]);
	const withinWalls =
		Math.abs(point.x) + ROBOT_RADIUS > ARENA.width / 2 ||
		Math.abs(point.z) + ROBOT_RADIUS > ARENA.height / 2;
	return withinWalls || collidesWithObstacle(point.x, point.z);
}

export function createBlockedCells() {
	const blocked = new Set();
	for (let y = 0; y < ARENA.height; y += 1) {
		for (let x = 0; x < ARENA.width; x += 1) {
			if (isBlocked([x, y])) blocked.add(cellKey([x, y]));
		}
	}
	return blocked;
}

class MinHeap {
	items = [];

	push(item) {
		const items = this.items;
		items.push(item);
		let index = items.length - 1;
		while (index > 0) {
			const parent = Math.floor((index - 1) / 2);
			if (items[parent].priority <= item.priority) break;
			items[index] = items[parent];
			index = parent;
		}
		items[index] = item;
	}

	pop() {
		const items = this.items;
		if (items.length === 0) return undefined;
		const first = items[0];
		const last = items.pop();
		if (items.length > 0 && last) {
			let index = 0;
			while (true) {
				const left = index * 2 + 1;
				const right = left + 1;
				if (left >= items.length) break;
				const child =
					right < items.length &&
					items[right].priority < items[left].priority
						? right
						: left;
				if (items[child].priority >= last.priority) break;
				items[index] = items[child];
				index = child;
			}
			items[index] = last;
		}
		return first;
	}

	get size() {
		return this.items.length;
	}
}

export function findPath(start, goal, blocked) {
	if (
		start[0] < 0 ||
		start[0] >= ARENA.width ||
		start[1] < 0 ||
		start[1] >= ARENA.height ||
		goal[0] < 0 ||
		goal[0] >= ARENA.width ||
		goal[1] < 0 ||
		goal[1] >= ARENA.height ||
		blocked.has(cellKey(start)) ||
		blocked.has(cellKey(goal))
	) {
		return null;
	}

	const startKey = cellKey(start);
	const goalKey = cellKey(goal);
	const frontier = new MinHeap();
	const cameFrom = new Map();
	const costs = new Map([[startKey, 0]]);
	frontier.push({ cell: start, key: startKey, cost: 0, priority: manhattan(start, goal) });

	while (frontier.size > 0) {
		const current = frontier.pop();
		if (!current || current.cost !== costs.get(current.key)) continue;
		if (current.key === goalKey) {
			const path = [goal];
			let key = goalKey;
			while (key !== startKey) {
				const previous = cameFrom.get(key);
				if (!previous) return null;
				path.push(previous.cell);
				key = previous.key;
			}
			return path.reverse();
		}

		for (const [dx, dy] of DIRECTIONS) {
			const next = [current.cell[0] + dx, current.cell[1] + dy];
			if (
				next[0] < 0 ||
				next[0] >= ARENA.width ||
				next[1] < 0 ||
				next[1] >= ARENA.height
			) {
				continue;
			}
			const nextKey = cellKey(next);
			const nextCost = current.cost + 1;
			if (
				blocked.has(nextKey) ||
				nextCost >= (costs.get(nextKey) ?? Number.POSITIVE_INFINITY)
			) {
				continue;
			}
			costs.set(nextKey, nextCost);
			cameFrom.set(nextKey, { cell: current.cell, key: current.key });
			frontier.push({
				cell: next,
				key: nextKey,
				cost: nextCost,
				priority: nextCost + manhattan(next, goal),
			});
		}
	}

	return null;
}

export function nearestOpenCell(point, blocked) {
	let closest = null;
	let closestDistance = Number.POSITIVE_INFINITY;
	for (let y = 0; y < ARENA.height; y += 1) {
		for (let x = 0; x < ARENA.width; x += 1) {
			const cell = [x, y];
			if (blocked.has(cellKey(cell))) continue;
			const distance = distanceSquared(point, cell);
			if (distance < closestDistance) {
				closest = cell;
				closestDistance = distance;
			}
		}
	}
	return closest;
}

export function chooseEscapeCell(current, pursuer, blocked) {
	const candidates = [current];
	for (const [dx, dy] of DIRECTIONS) {
		const candidate = [current[0] + dx, current[1] + dy];
		if (
			candidate[0] >= 0 &&
			candidate[0] < ARENA.width &&
			candidate[1] >= 0 &&
			candidate[1] < ARENA.height &&
			!blocked.has(cellKey(candidate))
		) {
			candidates.push(candidate);
		}
	}

	let safest = current;
	for (const candidate of candidates) {
		if (distanceSquared(candidate, pursuer) > distanceSquared(safest, pursuer)) {
			safest = candidate;
		}
	}
	return safest;
}

export class AuraTagGame {
	constructor() {
		this.blocked = createBlockedCells();
		this.openCells = [];
		for (let y = 0; y < ARENA.height; y += 1) {
			for (let x = 0; x < ARENA.width; x += 1) {
				if (!this.blocked.has(cellKey([x, y]))) this.openCells.push([x, y]);
			}
		}
		this.reset();
	}

	reset() {
		this.robot = cellToWorld(START_CELL);
		this.targetCell = [...TARGET_START_CELL];
		this.target = cellToWorld(this.targetCell);
		this.phase = "idle";
		this.remaining = CHASE_TIME_LIMIT;
		this.targetTimer = 0;
		this.winner = null;
		this.orbs = [];
		this.orbSpawnTimer = 0;
		this.orbSpawnCount = 0;
		this.activePowerUp = null;
		this.powerUpRemaining = 0;
		this.isJumping = false;
		this.message = "Press Start, then use WASD or the arrow keys to tag the red object.";
	}

	start() {
		if (this.phase === "finished") this.reset();
		if (this.phase !== "idle") return;
		this.phase = "aura-chasing";
		this.remaining = CHASE_TIME_LIMIT;
		this.message = "Use WASD or the arrow keys to drive AURA and tag the red object!";
	}

	update(deltaSeconds, input = { x: 0, z: 0 }) {
		if (this.phase === "idle" || this.phase === "finished") return;
		const dt = clamp(deltaSeconds, 0, 0.05);
		this.updatePowerUps(dt);
		this.moveRobot(input, dt);
		this.collectOrb();

		if (this.phase === "aura-chasing") {
			if (this.isTagged()) {
				this.finish("AURA");
				return;
			}
			this.remaining = Math.max(0, this.remaining - dt);
			if (this.remaining === 0) {
				this.phase = "red-chasing";
				this.path = [];
				this.targetTimer = 0;
				this.message = "Time's up! The red object is chasing AURA—run!";
			}
		}

		if (this.phase === "aura-chasing" || this.phase === "red-chasing") {
			this.targetTimer += dt;
			while (this.targetTimer >= TARGET_STEP_INTERVAL) {
				this.targetTimer -= TARGET_STEP_INTERVAL;
				this.moveTarget();
				if (this.isTagged()) {
					this.finish(this.phase === "aura-chasing" ? "AURA" : "RED");
					return;
				}
			}
		}

		if (this.phase === "red-chasing" && this.isTagged()) {
			this.finish("RED");
		}
	}

	updatePowerUps(dt) {
		this.orbSpawnTimer += dt;
		if (this.orbSpawnTimer >= ORB_SPAWN_INTERVAL) {
			this.orbSpawnTimer -= ORB_SPAWN_INTERVAL;
			this.spawnOrb();
		}

		if (this.powerUpRemaining > 0) {
			this.powerUpRemaining = Math.max(0, this.powerUpRemaining - dt);
			if (this.powerUpRemaining === 0) this.activePowerUp = null;
		}
	}

	spawnOrb() {
		const safeCells = this.openCells.filter(([x, y]) => {
			const position = cellToWorld([x, y]);
			return (
				distanceSquared([position.x, position.z], [this.robot.x, this.robot.z]) > 16 &&
				distanceSquared([position.x, position.z], [this.target.x, this.target.z]) > 16
			);
		});
		const candidates = safeCells.length > 0 ? safeCells : this.openCells;
		const leftCells = candidates.filter(([x]) => x < ARENA.width / 2);
		const rightCells = candidates.filter(([x]) => x >= ARENA.width / 2);
		let farthestPair = null;
		let farthestDistance = -1;
		for (const leftCell of leftCells) {
			for (const rightCell of rightCells) {
				const distance = distanceSquared(leftCell, rightCell);
				if (distance > farthestDistance) {
					farthestPair = [leftCell, rightCell];
					farthestDistance = distance;
				}
			}
		}
		const [leftCell, rightCell] = farthestPair ?? [
			candidates[0],
			candidates.at(-1),
		];
		const speedOnLeft = this.orbSpawnCount % 2 === 0;
		this.orbSpawnCount += 1;
		this.orbs = [
			{
				type: speedOnLeft ? "speed" : "jump",
				position: cellToWorld(leftCell),
			},
			{
				type: speedOnLeft ? "jump" : "speed",
				position: cellToWorld(rightCell),
			},
		];
		this.message = "Two power orbs appeared on opposite sides of the arena!";
	}

	collectOrb() {
		const collectedIndex = this.orbs.findIndex(
			(orb) =>
				Math.hypot(
					this.robot.x - orb.position.x,
					this.robot.z - orb.position.z,
				) <= ORB_PICKUP_DISTANCE,
		);
		if (collectedIndex === -1) return;

		const [orb] = this.orbs.splice(collectedIndex, 1);
		this.activePowerUp = orb.type;
		this.powerUpRemaining = POWER_UP_DURATION;
		this.message =
			this.activePowerUp === "speed"
				? "Speed boost collected! AURA moves 2x faster for 5 seconds."
				: "Jump boost collected! AURA can jump over the opponent for 5 seconds.";
	}

	moveTarget() {
		if (this.phase === "aura-chasing") {
			const pursuer = [
				this.robot.x + ARENA.width / 2 - 0.5,
				this.robot.z + ARENA.height / 2 - 0.5,
			];
			const next = chooseEscapeCell(this.targetCell, pursuer, this.blocked);
			if (cellKey(next) === cellKey(this.targetCell)) return;
			this.targetCell = next;
			this.target = cellToWorld(next);
			return;
		}

		const robotCell = nearestOpenCell(worldToCell(this.robot), this.blocked);
		if (!robotCell) return;
		const path = findPath(this.targetCell, robotCell, this.blocked);
		if (!path || path.length < 2) return;
		this.targetCell = path[1];
		this.target = cellToWorld(this.targetCell);
	}

	moveRobot(input, dt) {
		const magnitude = Math.hypot(input.x, input.z);
		if (magnitude === 0) return;
		const speedMultiplier = this.activePowerUp === "speed" ? 2 : 1;
		const scale = (ROBOT_SPEED * speedMultiplier * dt) / Math.max(1, magnitude);
		const dx = input.x * scale;
		const dz = input.z * scale;
		this.tryMoveRobot(this.robot.x + dx, this.robot.z);
		this.tryMoveRobot(this.robot.x, this.robot.z + dz);
	}

	tryMoveRobot(x, z) {
		const withinArena =
			Math.abs(x) + ROBOT_RADIUS <= ARENA.width / 2 &&
			Math.abs(z) + ROBOT_RADIUS <= ARENA.height / 2;
		if (withinArena && !collidesWithObstacle(x, z)) {
			this.robot = { x, z };
		}
	}

	isTagged() {
		const distance = Math.hypot(
			this.robot.x - this.target.x,
			this.robot.z - this.target.z,
		);
		this.isJumping = this.activePowerUp === "jump" && distance <= TAG_DISTANCE * 2;
		return distance <= TAG_DISTANCE && !this.isJumping;
	}

	finish(winner) {
		this.phase = "finished";
		this.winner = winner;
		this.message =
			winner === "AURA"
				? "AURA tagged the red object! AURA wins."
				: "The red object tagged AURA! Red wins.";
	}
}
