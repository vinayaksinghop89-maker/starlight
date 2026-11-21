import assert from 'node:assert/strict';
import test from 'node:test';

import {
	AuraTagGame,
	cellToWorld,
	createBlockedCells,
	findPath,
	worldToCell,
} from './aura-game.js';

test('grid and world coordinates round-trip at cell centers', () => {
	const cell = [7, 12];
	assert.deepEqual(worldToCell(cellToWorld(cell)), cell);
});

test('A* returns a safe route through the arena', () => {
	const blocked = createBlockedCells();
	const path = findPath([3, 3], [28, 14], blocked);

	assert.ok(path);
	assert.deepEqual(path[0], [3, 3]);
	assert.deepEqual(path.at(-1), [28, 14]);
	assert.ok(path.every(([x, y]) => !blocked.has(`${x},${y}`)));
	for (let index = 1; index < path.length; index += 1) {
		assert.equal(
			Math.abs(path[index][0] - path[index - 1][0]) +
				Math.abs(path[index][1] - path[index - 1][1]),
			1,
		);
	}
});

test('AURA gets one minute before the red object chases back', () => {
	const game = new AuraTagGame();
	game.start();
	game.remaining = 0.01;

	game.update(0.02);

	assert.equal(game.phase, 'red-chasing');
	assert.equal(game.winner, null);
});

test('AURA moves only in response to player input during the tag chase', () => {
	const game = new AuraTagGame();
	game.start();
	const startPosition = { ...game.robot };

	game.update(0.05);
	assert.deepEqual(game.robot, startPosition);

	game.update(0.05, { x: 1, z: 0 });
	assert.ok(game.robot.x > startPosition.x);
	assert.equal(game.robot.z, startPosition.z);
});

test('AURA wins by touching the target during its chase', () => {
	const game = new AuraTagGame();
	game.start();
	game.robot = { ...game.target };

	game.update(0.016);

	assert.equal(game.phase, 'finished');
	assert.equal(game.winner, 'AURA');
});

test('the red object wins by touching AURA after the role swap', () => {
	const game = new AuraTagGame();
	game.start();
	game.phase = 'red-chasing';
	game.robot = { ...game.target };

	game.update(0.016);

	assert.equal(game.phase, 'finished');
	assert.equal(game.winner, 'RED');
});

test('speed and jump orbs spawn together on opposite arena sides every 30 seconds', () => {
	const game = new AuraTagGame();
	game.start();
	game.orbSpawnTimer = 29.95;

	game.update(0.05);
	assert.deepEqual(
		game.orbs.map(({ type }) => type).sort(),
		['jump', 'speed'],
	);
	assert.ok(game.orbs[0].position.x * game.orbs[1].position.x < 0);
});

test('collecting a speed orb doubles AURA speed for 5 seconds', () => {
	const game = new AuraTagGame();
	game.start();
	game.robot = { x: -5, z: -8 };
	game.orbs = [{ type: 'speed', position: { ...game.robot } }];

	game.update(0.016);
	assert.equal(game.activePowerUp, 'speed');
	assert.equal(game.powerUpRemaining, 5);
	game.robot = { x: -5, z: -8 };
	game.moveRobot({ x: 1, z: 0 }, 0.05);

	assert.equal(game.robot.x, -5 + 7.6 * 2 * 0.05);
	assert.equal(game.orbs.length, 0);
});

test('a jump orb lets AURA leap over the opponent without being tagged', () => {
	const game = new AuraTagGame();
	game.start();
	game.robot = cellToWorld([3, 3]);
	game.orbs = [{ type: 'jump', position: { ...game.robot } }];
	game.target = { x: game.robot.x + 0.4, z: game.robot.z };

	game.update(0.016);

	assert.equal(game.activePowerUp, 'jump');
	assert.equal(game.powerUpRemaining, 5);
	assert.equal(game.isJumping, true);
	assert.equal(game.phase, 'aura-chasing');
	assert.equal(game.isTagged(), false);
});

test('power-ups expire after 5 seconds', () => {
	const game = new AuraTagGame();
	game.start();
	game.activePowerUp = 'speed';
	game.powerUpRemaining = 0.01;

	game.update(0.02);

	assert.equal(game.activePowerUp, null);
	assert.equal(game.powerUpRemaining, 0);
});
