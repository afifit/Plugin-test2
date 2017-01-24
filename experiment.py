#Full Name:afifit
#E-Mail: <dorafifitcohen@gmail.com>
#Time: Tue Jan 24 22:32:55 2017 +0200
import csv

from run_game import GameRunner

if __name__ == '__main__':
    players = ['simple_player', 'improved_player', 'better_h_player', 'improved_better_h_player']
    winner = GameRunner(2, 10, 5, 'n', 'better_h_player', 'simple_player').run()
    if winner[0] == 'red':
        redScore = 1
        blackScore = 0
    elif winner[0] == 'black':
        redScore = 0
        blackScore = 1
    else:
        redScore = 0.5
        blackScore = 0.5
    print(redScore, blackScore)
    '''
    T = [2, 10, 50]
    for time in T:
        for playerRed in players:
            for playerBlack in players:
                if playerRed != playerBlack:
                    winner = GameRunner(2, time, 5, 'n', playerRed, playerBlack).run()
                    if winner[0] == 'red':
                        redScore = 1
                        blackScore = 0
                    elif winner[0] == 'black':
                        redScore = 0
                        blackScore = 1
                    else:
                        redScore = 0.5
                        blackScore = 0.5
                    with open('experiment new new.csv', 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow([playerRed, playerBlack, time, redScore, blackScore])
'''''